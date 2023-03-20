# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from typing import Optional
from unittest.mock import mock_open

import pytest
from quri_parts.backend import BackendError
from quri_parts.circuit import QuantumCircuit

from quri_parts.riqu.backend.rest import Job, JobApi, JobsBody
from quri_parts.riqu.backend.rest.models import InlineResponse201
from quri_parts.riqu.backend.sampling import (
    RiquConfig,
    RiquSamplingBackend,
    RiquSamplingJob,
    RiquSamplingResult,
)

config_file_data = """[default]
url=default_url
api_token=default_api_token

[test]
url=test_url
api_token=test_api_token

[wrong]
url=test_url
"""

qasm_data = """OPENQASM 3;
include "stdgates.inc";
qubit[2] q;

h q[0];
cx q[0], q[1];"""


def get_dummy_job(status: str = "success") -> Job:
    job = Job(
        id="dummy_id",
        qasm="dummy_qasm",
        transpiled_qasm="dummy_transpiled_qasm",
        use_transpiler=True,
        shots=10000,
        status=status,
        result='{"counts": {"00": 6000, "10": 4000}}',
        created="dummy_created",
        ended="dummy_ended",
        remark="dummy_remark",
    )
    return job


def get_dummy_jobs_body(
    use_transpiler: bool = True, remark: Optional[str] = None
) -> JobsBody:
    jobs_body = JobsBody(
        qasm=qasm_data,
        use_transpiler=use_transpiler,
        shots=10000,
        remark=remark,
    )
    return jobs_body


def get_dummy_config() -> RiquConfig:
    config = RiquConfig("dummpy_url", "dummy_api_token")
    return config


class TestRiquSamplingResult:
    def test_init_error(self):
        # case: counts does not exist in result
        result_dict = dict()
        with pytest.raises(ValueError):
            RiquSamplingResult(result_dict)

    def test_counts(self):
        # Arrange
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            }
        }
        result = RiquSamplingResult(result_dict)

        # Act
        actual = result.counts

        # Assert
        expected = {
            0: 6000,
            2: 4000,
        }
        assert actual == expected


class TestRiquSamplingJob:
    def test_init_error(self):
        # case: job is None
        with pytest.raises(ValueError):
            RiquSamplingJob(job=None, job_api="dummy")

        # case: job_api is None
        job_raw = Job()
        with pytest.raises(ValueError):
            RiquSamplingJob(job=job_raw, job_api=None)

    def test_properties(self):
        # Arrange
        job_raw = get_dummy_job()
        job = RiquSamplingJob(job=job_raw, job_api="dummy")

        # Act & Assert
        assert job.id == "dummy_id"
        assert job.qasm == "dummy_qasm"
        assert job.transpiled_qasm == "dummy_transpiled_qasm"
        assert job.use_transpiler is True
        assert job.shots == 10000
        assert job.status == "success"
        assert job.result().counts == {0: 6000, 2: 4000}
        assert job.created == "dummy_created"
        assert job.ended == "dummy_ended"
        assert job.remark == "dummy_remark"

    def test_refresh(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        job.refresh()

        # Assert
        assert job.status == "success"

    def test_wait_for_completion(self, mocker):
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("success"),
                get_dummy_job("failure"),
                get_dummy_job("cancelled"),
            ],
        )

        # case1: status is "success"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.wait_for_completion()

        # Assert
        assert actual is not None
        assert actual.status == "success"

        # case2: status is "failure"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.wait_for_completion()

        # Assert
        assert actual is not None
        assert actual.status == "failure"

        # case3: status is "cancelled"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.wait_for_completion()

        # Assert
        assert actual is not None
        assert actual.status == "cancelled"

    def test_wait_for_completion__wait(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("processing"),
                get_dummy_job("success"),
            ],
        )

        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        start_time = time.time()
        actual = job.wait_for_completion(wait=3.0)
        elapsed_time = time.time() - start_time

        # Assert
        assert actual is not None
        assert actual.status == "success"
        assert elapsed_time >= 3.0

    def test_wait_for_completion__timeout(self, mocker):
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
            ],
        )

        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        start_time = time.time()
        actual = job.wait_for_completion(timeout=10.0, wait=3.0)
        elapsed_time = time.time() - start_time

        # Assert
        assert actual is None
        assert elapsed_time >= 10.0

    def test_result(self, mocker):
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("success"),
                get_dummy_job("failure"),
                get_dummy_job("cancelled"),
            ],
        )

        # case1: status is "success"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.result()

        # Assert
        assert actual.counts == {0: 6000, 2: 4000}

        # case2: status is "failure"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.wait_for_completion()

        # Assert
        assert actual is not None

        # case3: status is "cancelled"
        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        actual = job.wait_for_completion()

        # Assert
        assert actual is not None

    def test_result__wait(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("processing"),
                get_dummy_job("success"),
            ],
        )

        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act
        start_time = time.time()
        actual = job.result(wait=3.0)
        elapsed_time = time.time() - start_time

        # Assert
        assert actual.counts == {0: 6000, 2: 4000}
        assert elapsed_time >= 3.0

    def test_result__timeout(self, mocker):
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job",
            side_effect=[
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
                get_dummy_job("processing"),
            ],
        )

        # Arrange
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())
        assert job.status == "processing"

        # Act & Assert
        with pytest.raises(BackendError):
            job.result(timeout=10.0, wait=3.0)

    def test_cancel(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.put_jobs_job_id_cancel",
            return_value=None,
        )
        job_raw = get_dummy_job("processing")
        job = RiquSamplingJob(job=job_raw, job_api=JobApi())

        # Act
        job.cancel()

        # Assert
        mock_obj.assert_called_once_with("dummy_id")


class TestRiquConfig:
    def test_init_error(self):
        # case: counts does not exist in result
        result_dict = dict()
        with pytest.raises(ValueError):
            RiquSamplingResult(result_dict)

    def test_from_file(self, mocker):
        # Arrange
        mocker.patch("builtins.open", mock_open(read_data=config_file_data))

        # Act
        actual = RiquConfig.from_file()

        # Assert
        assert actual["url"] == "default_url"
        assert actual["api_token"] == "default_api_token"

    def test_from_file__section(self, mocker):
        # Arrange
        mocker.patch("builtins.open", mock_open(read_data=config_file_data))

        # Act
        actual = RiquConfig.from_file(section="test")

        # Assert
        assert actual["url"] == "test_url"
        assert actual["api_token"] == "test_api_token"

    def test_from_file__wrong(self, mocker):
        # Arrange
        mocker.patch("builtins.open", mock_open(read_data=config_file_data))

        # case: section is not found
        # Act & Assert
        with pytest.raises(KeyError):
            RiquConfig.from_file(section="not found")

        # case: api_key is not found
        # Act & Assert
        with pytest.raises(KeyError):
            RiquConfig.from_file(section="wrong")

    def test_properties(self):
        # Act
        actual = RiquConfig("dummpy_url", "dummy_api_token")

        # Assert
        assert actual.url == "dummpy_url"
        assert actual.api_token == "dummy_api_token"


class TestRiquSamplingBackend:
    def test_sample(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        # Act
        job = backend.sample(circuit, n_shots=10000)

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(body=get_dummy_jobs_body())

    def test_sample__use_transpiler(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        # Act
        job = backend.sample(circuit, n_shots=10000, use_transpiler=False)

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(body=get_dummy_jobs_body(use_transpiler=False))

    def test_sample__remark(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        # Act
        job = backend.sample(circuit, n_shots=10000, remark="dummy_remark")

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(
            body=get_dummy_jobs_body(remark="dummy_remark")
        )

    def test_retrieve_job(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        # Act
        job = backend.retrieve_job("job_id")

        # Assert
        assert type(job) == RiquSamplingJob
        assert job.id == "dummy_id"
        assert job.qasm == "dummy_qasm"
        assert job.transpiled_qasm == "dummy_transpiled_qasm"
        assert job.use_transpiler is True
        assert job.shots == 10000
        assert job.status == "success"
        assert job.result().counts == {0: 6000, 2: 4000}
        assert job.created == "dummy_created"
        assert job.ended == "dummy_ended"
        assert job.remark == "dummy_remark"
