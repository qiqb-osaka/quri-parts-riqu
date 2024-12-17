# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import base64
import io
import os
import zipfile
from typing import Optional
from unittest.mock import mock_open

import pytest
from quri_parts.backend import BackendError

from quri_parts.riqu.backend import RiquConfig, RiquSseJob
from quri_parts.riqu.rest import Job, JobsBody

# class MockJobApiClient():
#     def __init__(self, configuration=None, header_name=None, header_value=None):
#         self.configuration = configuration
#         self.header_name = header_name
#         self.header_value = header_value
#     def __del__(self):
#         pass
#     def from_file(self, section=None, path=None):
#         return None


class MockRiquSamplingJob:
    def __init__(self, id=None):
        self.job_id = id

    @property
    def id(self):
        return self.job_id


# Define MockJobApi instead of mocking JobApi to avoid bad file descriptor
class MockJobApi:
    def __init__(self, api_client=None):
        self.api_client = api_client

    def setReturn(self, ret, exception=None):
        self.returnValue = ret
        self.exception = exception
        return self

    def post_ssejob(self, up_file=None, job_type=None, remark=None):
        assert job_type == "sse"
        self.called_upfile = up_file
        self.remark = remark
        # return {"job_id": "dummy_id"}
        if self.exception:
            raise self.exception
        else:
            return self.returnValue

    def download_file(self, job_id=None):
        self.called_jobid = job_id
        if self.exception:
            raise self.exception
        else:
            return self.returnValue

    def assert_download_file(self, expected):
        assert self.called_jobid == expected

    def assert_post_ssejob(self, expected):
        assert self.called_upfile == expected


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
        transpiler="normal",
        shots=10000,
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
    transpiler: Optional[str] = "normal",
    remark: Optional[str] = None,
) -> JobsBody:
    jobs_body = JobsBody(
        qasm=qasm_data,
        transpiler=transpiler,
        shots=10000,
        remark=remark,
    )
    return jobs_body


def get_dummy_base64zip() -> str:
    zip_stream = io.BytesIO()
    dummy_zip = zipfile.ZipFile(zip_stream, "w", compression=zipfile.ZIP_DEFLATED)
    dummy_zip.writestr("dummy.log", "dumm_text")
    dummy_zip.close()
    encoded = base64.b64encode(zip_stream.getvalue()).decode()
    return encoded, zip_stream.getvalue()


def get_dummy_config() -> RiquConfig:
    config = RiquConfig("dummpy_url", "dummy_api_token")
    return config


class TestRiquSseJob:
    def test_init(self):
        # Arrange
        config = get_dummy_config()

        # Act
        sse_job = RiquSseJob(config)

        # Assert
        assert sse_job.config == config
        assert sse_job.job is None
        assert sse_job._job_api.api_client.configuration.host == config.url

    def test_init_default(self, mocker):
        # Arrange
        config = RiquConfig("dummpy_url_def", "dummy_api_token_def")
        mock_obj = mocker.patch(
            "quri_parts.riqu.backend.RiquConfig.from_file",
            return_value=config,
        )

        # Act
        sse_job = RiquSseJob()
        assert sse_job.config == config
        assert sse_job.job is None
        assert sse_job._job_api.api_client.configuration.host == config.url
        mock_obj.assert_called_once()

    def test_run_sse(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=9 * 1024 * 1024
        )

        job = MockRiquSamplingJob()
        mocker.patch(
            "quri_parts.riqu.backend.sse.RiquSamplingBackend.retrieve_job",
            return_value=job,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job._job_api = MockJobApi().setReturn(
            ret={"job_id": "dummy_id"}, exception=None
        )

        # Act
        ret_job = sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert ret_job == job
        sse_job._job_api.assert_post_ssejob("dummy/dummy.py")

    def test_run_sse_invalid_arg(self):
        # Act
        sse_job = RiquSseJob(get_dummy_config())
        with pytest.raises(ValueError) as e:
            sse_job.run_sse(None)

        # Assert
        assert str(e.value) == "file_path is not set."

    def test_run_sse_nofile(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=False)
        sse_job = RiquSseJob(get_dummy_config())

        # Act
        with pytest.raises(ValueError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == "The file does not exist: dummy/dummy.py"

    def test_run_invalid_extention(self, mocker):
        pass
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=10 * 1024 * 1024
        )
        sse_job = RiquSseJob(get_dummy_config())

        # Act
        with pytest.raises(ValueError) as e:
            sse_job.run_sse("dummy/dummy.y")

        # Assert
        assert str(e.value) == "The file is not python file: dummy/dummy.y"

    def test_run_largefile(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=10 * 1024 * 1024
        )
        sse_job = RiquSseJob(get_dummy_config())

        # Act
        with pytest.raises(ValueError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == f"file size is larger than {10*1024*1024}"

    def test_run_request_failure(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=9 * 1024 * 1024
        )
        sse_job = RiquSseJob(get_dummy_config())
        sse_job._job_api = MockJobApi().setReturn(ret=None, exception=Exception())

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == f"To perform sse on riqu server is failed."
        sse_job._job_api.assert_post_ssejob("dummy/dummy.py")

    def test_run_invalid_response(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=9 * 1024 * 1024
        )
        sse_job = RiquSseJob(get_dummy_config())
        sse_job._job_api = MockJobApi().setReturn(
            ret={"dummy": "dummy_id"}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == f"To perform sse on riqu server is failed."
        sse_job._job_api.assert_post_ssejob("dummy/dummy.py")

    def test_run_invalid_response_None(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=9 * 1024 * 1024
        )
        sse_job = RiquSseJob(get_dummy_config())
        sse_job._job_api = MockJobApi().setReturn(ret=None, exception=None)

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == f"To perform sse on riqu server is failed."
        sse_job._job_api.assert_post_ssejob("dummy/dummy.py")

    def test_run_retreive_failure(self, mocker):
        # Arrange
        # mocker.patch("quri_parts.riqu.backend.sampling.ApiClient", new=MockJobApiClient)
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=True)
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.getsize", return_value=9 * 1024 * 1024
        )
        mocker.patch(
            "quri_parts.riqu.backend.sse.RiquSamplingBackend.retrieve_job",
            side_effect=Exception("dummy error"),
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job._job_api = MockJobApi().setReturn(
            ret={"job_id": "dummy_id"}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.run_sse("dummy/dummy.py")

        # Assert
        assert str(e.value) == f"To perform sse on riqu server is failed."
        sse_job._job_api.assert_post_ssejob("dummy/dummy.py")

    def test_download_log(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=False)
        open_mock = mocker.patch("builtins.open", new_callable=mocker.mock_open)

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": "dummy.zip"}, exception=None
        )

        # Act
        path = sse_job.download_log()

        # Assert
        handle = open_mock()
        handle.write.assert_called_once_with(zip_bytes)
        assert path == os.path.join(os.getcwd(), "dummy.zip")
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_with_jobid(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=False)
        open_mock = mocker.patch("builtins.open", new_callable=mocker.mock_open)

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": "dummy.zip"}, exception=None
        )

        # Act
        path = sse_job.download_log(job_id="dummy_id2")

        # Assert
        handle = open_mock()
        handle.write.assert_called_once_with(zip_bytes)
        assert path == os.path.join(os.getcwd(), "dummy.zip")
        sse_job._job_api.assert_download_file("dummy_id2")

    def test_download_log_invalid_jobid(self, mocker):
        # Arrange
        mocker.patch("quri_parts.riqu.backend.sse.os.path.exists", return_value=False)

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = None
        # Act
        with pytest.raises(ValueError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert str(e.value) == f"job_id is not set."

    def test_download_log_with_path(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )
        open_mock = mocker.patch("builtins.open", new_callable=mocker.mock_open)

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": "dummy.zip"}, exception=None
        )

        # Act
        path = sse_job.download_log(download_path="destination/path")

        # Assert
        open_mock.assert_called_once_with(
            os.path.join("destination/path", "dummy.zip"), "bw"
        )
        handle = open_mock()
        handle.write.assert_called_once_with(zip_bytes)
        assert path == os.path.join("destination/path", "dummy.zip")
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_path(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: False if path == "destination/path" else False,
        )

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": "dummy.zip"}, exception=None
        )

        # Act
        with pytest.raises(ValueError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert str(e.value) == f"The destination path does not exist: destination/path"
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_conflict_path(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else True,
        )

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": "dummy.zip"}, exception=None
        )

        # Act
        with pytest.raises(ValueError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert str(e.value) == f"The file already exists: destination/path/dummy.zip"
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_request_failure(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(ret=None, exception=Exception())

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert str(e.value) == f"To perform sse on riqu server is failed."
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_None(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        sse_job._job_api = MockJobApi().setReturn(ret=None, exception=None)

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_1(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## file is None
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": None, "filename": "dummy.zip"}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_2(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## filename is None
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": None}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_3(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## file is emtpy
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": "", "filename": "dummy.zip"}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_4(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        ## make zip stream to be downloaded
        encoded = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## filename is emtpy
        sse_job._job_api = MockJobApi().setReturn(
            ret={"file": encoded, "filename": ""}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_4(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## contains no file
        sse_job._job_api = MockJobApi().setReturn(
            ret={"filename": "dummy.zip"}, exception=None
        )

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")

    def test_download_log_invalid_response_5(self, mocker):
        # Arrange
        mocker.patch(
            "quri_parts.riqu.backend.sse.os.path.exists",
            side_effect=lambda path: True if path == "destination/path" else False,
        )

        ## make zip stream to be downloaded
        encoded, zip_bytes = get_dummy_base64zip()

        sse_job = RiquSseJob(get_dummy_config())
        sse_job.job = MockRiquSamplingJob(id="dummy_id")
        ## contains no filename
        sse_job._job_api = MockJobApi().setReturn(ret={"file": encoded}, exception=None)

        # Act
        with pytest.raises(BackendError) as e:
            sse_job.download_log(download_path="destination/path")

        # Assert
        assert (
            str(e.value)
            == f"To perform sse on riqu server is failed. The response does not contain valid file data."
        )
        sse_job._job_api.assert_download_file("dummy_id")
