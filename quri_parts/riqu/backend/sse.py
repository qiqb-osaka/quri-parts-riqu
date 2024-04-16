# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A module to run sse job on riqu server.
"""
import os
import base64
from typing import Optional

from quri_parts.backend import (
    BackendError
)

from .sampling import RiquSamplingBackend, RiquConfig, RiquSamplingJob
from ..rest import ApiClient, Configuration, JobApi

class RiquSseJob:
 
    def __init__(
        self,
        config: Optional[RiquConfig] = None
    ):
        # if config is None, load them from file
        if config is None:
            self.config = RiquConfig.from_file()
        else:
            self.config = config

        # construct JobApi
        rest_config = Configuration()
        rest_config.host = self.config.url
        if self.config.proxy:
            rest_config.proxy = self.config.proxy
        api_client = ApiClient(
            configuration=rest_config,
            header_name="q-api-token",
            header_value=self.config.api_token,
        )
        self._job_api: JobApi = JobApi(api_client=api_client)
        self.job = None

    def run_sse(
        self,
        file_path: str,
        remark: Optional[str] = ""
    ) -> RiquSamplingJob:
        # if file_path is not set, raise ValueError
        if file_path is None:
            raise ValueError("file_path is not set.")

        # if the file does not exist, raise ValueError
        if not os.path.exists(file_path):
            raise ValueError(f'The file does not exist: {file_path}')

        # get the base name and the extension of the file
        base_name, ext = os.path.splitext(file_path)

        # if the extension is not .py, raise ValueError
        if ext != ".py":
            raise ValueError(f"The file is not python file: {file_path}")

        max_file_size = 10 * 1024 * 1024 # 10MB

        # if the file size is larger than max_file_size, raise ValueError
        if os.path.getsize(file_path) >= max_file_size:
            raise ValueError(f"file size is larger than {max_file_size}")

        # set sse job type
        jobType = "sse"

        try:
            response = self._job_api.post_ssejob(up_file=file_path, remark=remark, job_type=jobType)

            job_id = response["job_id"]

            # make an instance of RiquSamplingBackend
            riqu_sampling_backend = RiquSamplingBackend(config=self.config)
            self.job = riqu_sampling_backend.retrieve_job(job_id=job_id)
        except Exception as e:
            raise BackendError("To perform sse on riqu server is failed.") from e

        return self.job
    
    def download_log(
            self,
            job_id: str = None,
            download_path: str = None,
        ) -> str:

        # if job_id is not set, raise ValueError
        if job_id is None:
            if self.job is not None:
                job_id = self.job.id
            else:
                raise ValueError("job_id is not set.")

        try:
            response = self._job_api.download_file(job_id=job_id)
        except Exception as e:
            raise BackendError("To perform sse on riqu server is failed.") from e

        if response is None or not "file" in response or not "filename" in response \
            or not response["file"] or not response["filename"]:
                raise BackendError("To perform sse on riqu server is failed. The response does not contain valid file data.")

        data = response["file"]
        filename = response["filename"]

        if download_path is None:
            download_path = os.getcwd()
        else:
            if not os.path.exists(download_path):
                raise ValueError(f"The destination path does not exist: {download_path}")

        file_path = os.path.join(download_path, filename)

        # if the file already exists, raise ValueError
        if os.path.exists(file_path):
            raise ValueError(f"The file already exists: {file_path}")

        # decode the base64 encoded data and write it to the file
        decoded_zip = base64.b64decode(data)
        with open(file_path, 'bw') as t_file:
            t_file.write(decoded_zip)

        return file_path
