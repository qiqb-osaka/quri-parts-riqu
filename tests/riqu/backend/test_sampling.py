# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import time
from typing import Dict, Optional
from unittest.mock import mock_open

import pytest
from quri_parts.backend import BackendError
from quri_parts.circuit import QuantumCircuit

from quri_parts.riqu.backend.sampling import (
    RiquConfig,
    RiquSamplingBackend,
    RiquSamplingJob,
    RiquSamplingResult,
)
from quri_parts.riqu.rest import Job, JobApi, JobsBody
from quri_parts.riqu.rest.models import InlineResponse201

config_file_data = """[default]
url=default_url
api_token=default_api_token

[test]
url=test_url
api_token=test_api_token

[option]
url=test_url
api_token=test_api_token
proxy=https://testproxy:port

[wrong]
url=test_url
"""

qasm_data = """OPENQASM 3;
include "stdgates.inc";
qubit[2] q;

h q[0];
cx q[0], q[1];"""

qasm_data2 = """OPENQASM 3;
include "stdgates.inc";
qubit[3] q;

h q[0];
cx q[0], q[1];
ry(0.1) q[2];"""

qasm_array_json = json.dumps({"qasm": [qasm_data, qasm_data2, qasm_data]})


def get_dummy_job(status: str = "success") -> Job:
    job = Job(
        id="dummy_id",
        qasm="dummy_qasm",
        transpiled_qasm="dummy_transpiled_qasm",
        transpiler="normal",
        shots=10000,
        job_type="normal",
        status=status,
        result='{"counts": {"00": 6000, "10": 4000}, "properties": { "0": {"qubit_index": 0, "measurement_window_index": 0}, "1": {"qubit_index": 1, "measurement_window_index": 0}}}',
        created="dummy_created",
        in_queue="dummy_in_queue",
        out_queue="dummy_out_queue",
        ended="dummy_ended",
        remark="dummy_remark",
    )
    return job


def get_dummy_jobs_body(
    qasm: Optional[str] = qasm_data,
    transpiler: Optional[str] = "normal",
    remark: Optional[str] = None,
    job_type: Optional[str] = None,
) -> JobsBody:
    jobs_body = JobsBody(
        qasm=qasm,
        transpiler=transpiler,
        shots=10000,
        remark=remark,
        job_type=job_type,
    )
    return jobs_body


def get_dummy_config() -> RiquConfig:
    config = RiquConfig("dummpy_url", "dummy_api_token")
    return config


class TestRiquSamplingResult:
    def test_init_error(self):
        # case: counts does not exist in result
        result_without_count = {
            "properties": {
                0: {"qubit_index": 0, "measurement_window_index": 0},
                1: {"qubit_index": 1, "measurement_window_index": 0},
            }
        }
        with pytest.raises(ValueError):
            RiquSamplingResult(result_without_count)

        # case: properties does not exist in result
        result_without_properties = {
            "counts": {
                0: 6000,
                2: 4000,
            }
        }
        with pytest.raises(ValueError):
            RiquSamplingResult(result_without_properties)

    def test_counts(self):
        # Arrange
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            },
            "properties": {
                0: {
                    "qubit_index": 0,
                    "measurement_window_index": 0,
                },
                1: {
                    "qubit_index": 1,
                    "measurement_window_index": 0,
                },
            },
            "transpiler_info": {
                "physical_virtual_mapping": {
                    "0": 1,
                    "1": 0,
                },
            },
            "message": "SUCCESS!",
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

    def test_properties(self):
        # Arrange
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            },
            "properties": {
                0: {
                    "qubit_index": 0,
                    "measurement_window_index": 0,
                },
                1: {
                    "qubit_index": 1,
                    "measurement_window_index": 0,
                },
            },
            "transpiler_info": {
                "physical_virtual_mapping": {
                    "0": 1,
                    "1": 0,
                },
            },
            "message": "SUCCESS!",
        }
        result = RiquSamplingResult(result_dict)

        # Act
        actual = result.properties

        # Assert
        expected = {
            0: {
                "qubit_index": 0,
                "measurement_window_index": 0,
            },
            1: {
                "qubit_index": 1,
                "measurement_window_index": 0,
            },
        }
        assert actual == expected

    def test_transpiler_info(self):
        # Arrange
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            },
            "properties": {
                0: {
                    "qubit_index": 0,
                    "measurement_window_index": 0,
                },
                1: {
                    "qubit_index": 1,
                    "measurement_window_index": 0,
                },
            },
            "transpiler_info": {
                "physical_virtual_mapping": {
                    "0": 1,
                    "1": 0,
                },
            },
            "message": "SUCCESS!",
        }
        result = RiquSamplingResult(result_dict)

        # Act
        actual = result.transpiler_info

        # Assert
        expected = {
            "physical_virtual_mapping": {
                "0": 1,
                "1": 0,
            },
        }
        assert actual == expected

    def test_message(self):
        # Arrange
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            },
            "properties": {
                0: {
                    "qubit_index": 0,
                    "measurement_window_index": 0,
                },
                1: {
                    "qubit_index": 1,
                    "measurement_window_index": 0,
                },
            },
            "transpiler_info": {
                "physical_virtual_mapping": {
                    "0": 1,
                    "1": 0,
                },
            },
            "message": "SUCCESS!",
        }
        result = RiquSamplingResult(result_dict)

        # Act
        actual = result.message

        # Assert
        expected = "SUCCESS!"
        assert actual == expected

    def test_repr(self):
        # Arrage
        result_dict = {
            "counts": {
                0: 6000,
                2: 4000,
            },
            "properties": {
                0: {
                    "qubit_index": 0,
                    "measurement_window_index": 0,
                },
                1: {
                    "qubit_index": 1,
                    "measurement_window_index": 0,
                },
            },
            "transpiler_info": {
                "physical_virtual_mapping": {
                    "0": 1,
                    "1": 0,
                },
            },
            "message": "SUCCESS!",
        }
        result = RiquSamplingResult(result_dict)

        # Act
        actual = result.__repr__()

        # Assert
        expected = str(result_dict)
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
        assert job.transpiler == "normal"
        assert job.shots == 10000
        assert job.job_type == "normal"
        assert job.status == "success"
        assert job.result().counts == {0: 6000, 2: 4000}
        assert job.result().properties == {
            0: {"qubit_index": 0, "measurement_window_index": 0},
            1: {"qubit_index": 1, "measurement_window_index": 0},
        }
        assert job.created == "dummy_created"
        assert job.in_queue == "dummy_in_queue"
        assert job.out_queue == "dummy_out_queue"
        assert job.ended == "dummy_ended"
        assert job.remark == "dummy_remark"

    def test_refresh(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
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
            "quri_parts.riqu.rest.JobApi.get_job",
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
            "quri_parts.riqu.rest.JobApi.get_job",
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
            "quri_parts.riqu.rest.JobApi.get_job",
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
            "quri_parts.riqu.rest.JobApi.get_job",
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
        assert actual.properties == {
            0: {"qubit_index": 0, "measurement_window_index": 0},
            1: {"qubit_index": 1, "measurement_window_index": 0},
        }

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
            "quri_parts.riqu.rest.JobApi.get_job",
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
        assert actual.properties == {
            0: {"qubit_index": 0, "measurement_window_index": 0},
            1: {"qubit_index": 1, "measurement_window_index": 0},
        }
        assert elapsed_time >= 3.0

    def test_result__timeout(self, mocker):
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job",
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
            "quri_parts.riqu.rest.JobApi.put_jobs_job_id_cancel",
            return_value=None,
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job",
            return_value=get_dummy_job("cancelled"),
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
        assert actual.url == "default_url"
        assert actual.api_token == "default_api_token"
        assert actual.proxy is None

    def test_from_file__section(self, mocker):
        # Arrange
        mocker.patch("builtins.open", mock_open(read_data=config_file_data))

        # Act
        actual = RiquConfig.from_file(section="test")

        # Assert
        assert actual.url == "test_url"
        assert actual.api_token == "test_api_token"
        assert actual.proxy is None

    def test_from_file__optional(self, mocker):
        # Arrange
        mocker.patch("builtins.open", mock_open(read_data=config_file_data))

        # Act
        actual = RiquConfig.from_file(section="option")

        # Assert
        assert actual.url == "test_url"
        assert actual.api_token == "test_api_token"
        assert actual.proxy == "https://testproxy:port"

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
        actual = RiquConfig("dummy_url", "dummy_api_token", "https://dummy:1234")

        # Assert
        assert actual.url == "dummy_url"
        assert actual.api_token == "dummy_api_token"
        assert actual.proxy == "https://dummy:1234"


class TestRiquSamplingBackend:
    def test_init__use_env(self, mocker):
        # Arrange
        def mock_getenv(key, default=None):
            if key == "RIQU_URL":
                return "dummy_url"
            elif key == "RIQU_API_TOKEN":
                return "dummy_api_token"
            elif key == "RIQU_PROXY":
                return "https://dummy:1234"
            return default

        mocker.patch("os.getenv", side_effect=mock_getenv)

        # Act
        backend = RiquSamplingBackend()

        # Assert
        api_client = backend._job_api.api_client
        assert api_client.configuration.host == "dummy_url"
        assert api_client.default_headers["q-api-token"] == "dummy_api_token"
        assert api_client.configuration.proxy == "https://dummy:1234"

    def test_init__not_use_env(self, mocker):
        # Arrange
        def mock_getenv(key, default=None):
            if key == "RIQU_URL":
                return "dummy_url"
            # RIQU_API_TOKEN isn't set
            # elif key == "RIQU_API_TOKEN":
            #     return "dummy_api_token"
            elif key == "RIQU_PROXY":
                return "https://dummy:1234"
            return default

        mocker.patch("os.getenv", side_effect=mock_getenv)
        mocker.patch(
            "quri_parts.riqu.backend.RiquConfig.from_file",
            return_value=RiquConfig("fake_url", "fake_token", "https://fake_proxy"),
        )

        # Act
        backend = RiquSamplingBackend()

        # Assert
        api_client = backend._job_api.api_client
        assert api_client.configuration.host == "fake_url"
        assert api_client.default_headers["q-api-token"] == "fake_token"
        assert api_client.configuration.proxy == "https://fake_proxy"

    def test_sample(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        # Act
        job = backend.sample(circuit, n_shots=10000)

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(body=get_dummy_jobs_body(job_type="normal"))

    def test_sample_circuit_array(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        circuit2 = QuantumCircuit(3)
        circuit2.add_H_gate(0)
        circuit2.add_CNOT_gate(0, 1)
        circuit2.add_RY_gate(2, 0.1)

        # Act
        job = backend.sample([circuit, circuit2, circuit], n_shots=10000)

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(
            body=get_dummy_jobs_body(qasm=qasm_array_json, job_type="multi_manual")
        )

    def test_sample__transpiler(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        # Act
        job = backend.sample(circuit, n_shots=10000, transpiler="normal")

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(
            body=get_dummy_jobs_body(transpiler="normal", job_type="normal")
        )

    def test_sample__remark(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
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
            body=get_dummy_jobs_body(remark="dummy_remark", job_type="normal")
        )

    def test_sample_qasm(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        # Act
        job = backend.sample_qasm(qasm_data, n_shots=10000)

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(body=get_dummy_jobs_body())

    def test_sample_qasm__transpiler(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        # Act
        job = backend.sample_qasm(qasm_data, n_shots=10000, transpiler="normal")

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(body=get_dummy_jobs_body(transpiler="normal"))

    def test_sample_qasm__remark(self, mocker):
        # Arrange
        mock_obj = mocker.patch(
            "quri_parts.riqu.rest.JobApi.post_job",
            return_value=InlineResponse201("dummy_id"),
        )
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        # Act
        job = backend.sample_qasm(qasm_data, n_shots=10000, remark="dummy_remark")

        # Assert
        assert job.id == "dummy_id"
        mock_obj.assert_called_once_with(
            body=get_dummy_jobs_body(remark="dummy_remark")
        )

    def test_retrieve_job(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.rest.JobApi.get_job", return_value=get_dummy_job()
        )
        backend = RiquSamplingBackend(get_dummy_config())

        # Act
        job = backend.retrieve_job("job_id")

        # Assert
        assert type(job) == RiquSamplingJob
        assert job.id == "dummy_id"
        assert job.qasm == "dummy_qasm"
        assert job.transpiled_qasm == "dummy_transpiled_qasm"
        assert job.transpiler == "normal"
        assert job.shots == 10000
        assert job.job_type == "normal"
        assert job.status == "success"
        assert job.result().counts == {0: 6000, 2: 4000}
        assert job.result().properties == {
            0: {"qubit_index": 0, "measurement_window_index": 0},
            1: {"qubit_index": 1, "measurement_window_index": 0},
        }
        assert job.created == "dummy_created"
        assert job.in_queue == "dummy_in_queue"
        assert job.out_queue == "dummy_out_queue"
        assert job.ended == "dummy_ended"
        assert job.remark == "dummy_remark"
