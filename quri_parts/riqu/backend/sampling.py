# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A module to perform sampling on riqu server.

Before sampling, sign up for riqu server and create a configuration file in
path ``~/.riqu``. See the description of :meth:`RiquConfig.from_file` method
for how to write ``~/.riqu`` file.

Examples:
    To perform sampling 1000 shots on riqu server, run the following code:

    .. highlight:: python
    .. code-block:: python

        from quri_parts.circuit import QuantumCircuit
        from quri_parts.riqu.backend import RiquSamplingBackend

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        backend = RiquSamplingBackend()
        job = backend.sample(circuit, n_shots=1000)
        counts = job.result().counts
        print(counts)

    To perform with the transpiler setting on riqu server, run the following code:

    .. highlight:: python
    .. code-block:: python

        from quri_parts.circuit import QuantumCircuit
        from quri_parts.riqu.backend import RiquSamplingBackend

        circuit = QuantumCircuit(2)
        circuit.add_H_gate(0)
        circuit.add_CNOT_gate(0, 1)

        backend = RiquSamplingBackend()
        job = backend.sample(circuit, n_shots=10000, transpiler="normal")
        counts = job.result().counts
        print(counts)

    The specifications of the transpiler setting is as follows:

    - ``"none"``: no transpiler
    - ``"pass"``: use the "do nothing transpiler" (same as ``"none"``)
    - ``"normal"``: use default transpiler (by default)

    You can also input OpenQASM 3.0 program.

    .. highlight:: python
    .. code-block:: python

        from quri_parts.circuit import QuantumCircuit
        from quri_parts.riqu.backend import RiquSamplingBackend

        qasm = \"\"\"OPENQASM 3;
        include "stdgates.inc";
        qubit[2] q;

        h q[0];
        cx q[0], q[1];\"\"\"

        backend = RiquSamplingBackend()
        job = backend.sample_qasm(qasm, n_shots=1000)
        counts = job.result().counts
        print(counts)
        
    To retrieve jobs already sent to riqu server, run the following code:

    .. highlight:: python
    .. code-block:: python

        from quri_parts.riqu.backend import RiquSamplingBackend

        job = backend.retrieve_job("<put target job id>")
        counts = job.result().counts
        print(counts)
"""

import configparser
import datetime
import json
import os
import time
from collections import Counter
from typing import Any, Optional, Dict, Union

from quri_parts.backend import (
    BackendError,
    SamplingBackend,
    SamplingCounts,
    SamplingJob,
    SamplingResult,
)
from quri_parts.circuit import NonParametricQuantumCircuit
from quri_parts.openqasm.circuit import convert_to_qasm_str

from ..rest import ApiClient, Configuration, Job, JobApi, JobsBody


JOB_FINAL_STATUS = ["success", "failure", "cancelled"]


class RiquSamplingResult(SamplingResult):
    """A result of a riqu sampling job.

    Args:
        result: A result of dict type.
            This dict should have the key ``counts``.
            The value of ``counts`` is the dict input for the counts.
            Where the keys represent a measured classical value
            and the value is an integer the number of shots with that result.

            If the keys of ``counts`` is expressed as a bit string,
            then ``properties`` is a mapping from the index of bit string
            to the index of the quantum circuit.

    Raises:
        ValueError: If ``counts`` or ``properties`` does not exist in result.

    Examples:
        An example of a dict of result is as below:

        .. code-block::

            {
                "counts": {
                    0: 600,
                    1: 300,
                    3: 100,
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

        In the above case, the bit string representation of 0, 1, and 3
        in the keys of ``counts`` is "00", "01", and "11" respectively.
        The index of these 2 bits is the key of ``properties``
        and the index of the quantum circuit is ``qubit_index``.
        The LSB (Least Significant Bit) of the bit string representation is ``index=0``.

        If the same ``qubit_index`` is measured multiple times in one quantum circuit,
        ``measurement_window_index`` are set to 0, 1, 2, ...

    """

    def __init__(self, result: dict[str, Any]) -> None:
        super().__init__()

        if "counts" not in result:
            raise ValueError("counts does not exist in result.")
        if "properties" not in result:
            raise ValueError("properties does not exist in result.")

        self._result = result
        self._counts = result.get("counts")
        self._properties = result.get("properties")
        self._transpiler_info = result.get("transpiler_info")
        self._message = result.get("message")
        self._divided_result = (
            result["divided_result"] if "divided_result" in result else None
        )

    @property
    def counts(self) -> SamplingCounts:
        """Returns the dict input for the counts."""
        return self._counts

    @property
    def properties(self) -> dict:
        """Returns properties."""
        return self._properties

    @property
    def transpiler_info(self) -> dict:
        """Returns transpiler_info."""
        return self._transpiler_info

    @property
    def message(self) -> str:
        """Returns message."""
        return self._message

    @property
    def divided_result(self) -> Dict:
        """Returns divided_result."""
        return self._divided_result

    def __repr__(self) -> str:
        return str(self._result)


class RiquSamplingJob(SamplingJob):
    """A job for a riqu sampling measurement.

    Args:
        Job: A result of dict type.
        job_api: A result of dict type.

    Raises:
        ValueError: If ``job`` or ``job_api`` is None.
    """

    def __init__(self, job: Job, job_api: JobApi):
        super().__init__()

        if job is None:
            raise ValueError("job should not be None.")
        self._job: Job = job

        if job_api is None:
            raise ValueError("job_api should not be None.")
        self._job_api: JobApi = job_api

    @property
    def id(self) -> str:
        """The id of the job."""
        return self._job.id

    @property
    def qasm(self) -> str:
        """The circuit converted to OpenQASM 3.0 format."""
        return self._job.qasm

    @property
    def transpiled_qasm(self) -> str:
        """The circuit in OpenQASM 3.0 format transpiled by riqu server."""
        return self._job.transpiled_qasm

    @property
    def transpiler(self) -> str:
        """The transpiler setting."""
        return self._job.transpiler

    @property
    def shots(self) -> int:
        """Number of repetitions of each circuit, for sampling."""
        return self._job.shots

    @property
    def job_type(self) -> str:
        """The type of Job."""
        return self._job.job_type

    @property
    def status(self) -> str:
        """The status of Job."""
        return self._job.status

    @property
    def created(self) -> datetime.datetime:
        """``datetime`` when riqu server received the new job."""
        return self._job.created

    @property
    def in_queue(self) -> datetime.datetime:
        """``datetime`` when the job is in queue."""
        return self._job.in_queue

    @property
    def out_queue(self) -> datetime.datetime:
        """``datetime`` when the job is out queue."""
        return self._job.out_queue

    @property
    def ended(self) -> datetime.datetime:
        """``datetime`` when the job is ended."""
        return self._job.ended

    @property
    def remark(self) -> str:
        """The remark to be assigned to the job."""
        return self._job.remark

    def refresh(self) -> None:
        """Retrieves the latest job information from riqu server."""
        try:
            self._job = self._job_api.get_job(self._job.id)
        except Exception as e:
            raise BackendError("To refresh job is failed.") from e

    def wait_for_completion(
        self, timeout: Optional[float] = None, wait: float = 10.0
    ) -> Optional[Job]:
        """Waits until the job progress to the end such as ``success`` or
        ``failure``, ``cancelled``.

        Args:
            timeout: The number of seconds to wait for job.
            wait: Time in seconds between queries.
        """
        start_time = time.time()
        self.refresh()
        while self._job.status not in JOB_FINAL_STATUS:
            # check timeout
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                return None

            # sleep and get job
            time.sleep(wait)
            self.refresh()

        return self._job

    def result(
        self, timeout: Optional[float] = None, wait: Optional[float] = 10.0
    ) -> SamplingResult:
        """Waits until the job progress to the end and returns the result of
        the job.

        If the status of job is not ``success``, ``failure``, or ``cancelled``,
        the job is retrieved from riqu server at intervals of ``wait`` seconds.
        If the job does not progress to the end after ``timeout`` seconds,
        raise :class:`BackendError`.

        Args:
            timeout: The number of seconds to wait for job.
            wait: Time in seconds between queries.

        Raises:
            BackendError: If job cannot be found or if an authentication error occurred
                or timeout occurs, etc.
        """
        if self._job.status not in JOB_FINAL_STATUS:
            job = self.wait_for_completion(timeout, wait)
            if job is None:
                raise BackendError(f"Timeout occurred after {timeout} seconds.")
            elif job.status in ["failure", "cancelled"]:
                raise BackendError(f"Job ended with status {job.status}.")
            else:
                self._job = job

        # edit json for RiquSamplingResult
        result = json.loads(self._job.result)
        result["counts"] = Counter(
            {int(bits, 2): count for bits, count in result["counts"].items()}
        )
        result["properties"] = {
            int(qubit_index): value
            for qubit_index, value in result["properties"].items()
        }
        if "divided_result" in result and result["divided_result"] is not None:
            result["divided_result"]: SamplingCounts = [
                dict(
                    {
                        int(bits, 2): count
                        for bits, count in result["divided_result"][one_result].items()
                    }
                )
                for one_result in result["divided_result"]
            ]

        return RiquSamplingResult(result)

    def cancel(self) -> None:
        """Cancels the job.

        If the job statuses are success, failure, or cancelled,
        then cannot be cancelled and an error occurs.

        Raises:
            BackendError: If job cannot be found or if an authentication error occurred
                or if job cannot be cancelled, etc.
        """
        try:
            self._job_api.put_jobs_job_id_cancel(self._job.id)
            self.refresh()
        except Exception as e:
            raise BackendError("To cancel job is failed.") from e

    def __repr__(self) -> str:
        return self._job.to_str()


class RiquConfig:
    """A configuration information class for using riqu backend.

    Args:
        url: Base URL for riqu server.
        api_token: API token for riqu server.

    Raises:
        ValueError: If ``url`` or ``api_token`` is None.
    """

    def __init__(self, url: str, api_token: str, proxy: Optional[str] = None) -> None:
        super().__init__()

        if url is None:
            raise ValueError("url should not be None.")
        self._url: str = url

        if api_token is None:
            raise ValueError("api_token should not be None.")
        self._api_token: str = api_token

        self._proxy: str = proxy

    @property
    def url(self) -> str:
        return self._url

    @property
    def api_token(self) -> str:
        return self._api_token

    @property
    def proxy(self) -> Optional[str]:
        return self._proxy

    @staticmethod
    def from_file(
        section: Optional[str] = "default", path: Optional[str] = "~/.riqu"
    ) -> "RiquConfig":
        """Reads configuration information from a file.

        Args:
            section: A :class:`RiquConfig` for circuit execution.
            path: A path for config file.

        Returns:
            Configuration information :class:`RiquConfig` .

        Examples:
            The riqu configuration file describes configuration information for each
            section. A section has a header in the form ``[section]``.
            The default file path is ``~/.riqu`` and the default section name is
            ``default``. Each section describes a setting in the format ``key=value``.
            An example of a configuration file description is as below:

            .. code-block::

                [default]
                url=<base URL>
                api_token=<API token>

                [sectionA]
                url=<base URL>
                api_token=<API token>

                [sectioB]
                url=<base URL>
                api_token=<API token>
                proxy=http://<proxy>:<port>

            If ``sectionA`` settings are to be used, initialize ``RiquSamplingBackend`` as follows

            .. code-block::

                backend = RiquSamplingBackend(RiquConfig.from_file("sectionA"))

        """
        path = os.path.expandvars(path)
        path = os.path.expanduser(path)
        parser = configparser.ConfigParser()
        parser.read(path, encoding="utf-8")
        config = RiquConfig(
            url=parser[section]["url"],
            api_token=parser[section]["api_token"],
            proxy=parser[section].get("proxy", None),
        )
        return config


class RiquSamplingBackend(SamplingBackend):
    """A riqu backend for a sampling measurement.

    Args:
        config: A :class:`RiquConfig` for circuit execution.
            If this parameter is None, ``default`` section in ``~/.riqu`` file is read.
    """

    def __init__(
        self,
        config: Optional[RiquConfig] = None,
    ):
        super().__init__()

        # if config is None, load them from file
        if config is None:
            config = RiquConfig.from_file()

        # construct JobApi
        rest_config = Configuration()
        rest_config.host = config.url
        if config.proxy:
            rest_config.proxy = config.proxy
        api_client = ApiClient(
            configuration=rest_config,
            header_name="q-api-token",
            header_value=config.api_token,
        )
        self._job_api: JobApi = JobApi(api_client=api_client)

    def sample(
        self,
        circuit: Union[NonParametricQuantumCircuit, list[NonParametricQuantumCircuit]],
        n_shots: int,
        transpiler: Optional[str] = "normal",
        remark: Optional[str] = None,
    ) -> SamplingJob:
        """Perform a sampling measurement of a circuit.

        The circuit is transpiled on riqu server.
        The QURI Parts transpiling feature is not supported.
        The circuit is converted to OpenQASM 3.0 format and sent to riqu server.

        Args:
            circuit: The circuit to be sampled.
            n_shots: Number of repetitions of each circuit, for sampling.
            transpiler: The transpiler setting.
            remark: The remark to be assigned to the job.

        Returns:
            The job to be executed.

        Raises:
            ValueError: If ``n_shots`` is not a positive integer.
            BackendError: If job is wrong or if an authentication error occurred, etc.
        """
        if isinstance(circuit, list):
            qasms_dict = {"qasm": [convert_to_qasm_str(c) for c in circuit]}
            qasm_str = json.dumps(qasms_dict)
            job_type = "multi_manual"
        else:
            qasm_str = convert_to_qasm_str(circuit)
            job_type = "normal"

        job = self.sample_qasm(qasm_str, n_shots, transpiler, remark, job_type)

        return job

    def sample_qasm(
        self,
        qasm: Union[str, list[str]],
        n_shots: int,
        transpiler: Optional[str] = "normal",
        remark: Optional[str] = None,
        job_type: Optional[str] = None,
    ) -> SamplingJob:
        """Perform a sampling measurement of a OpenQASM 3.0 program.

        The OpenQASM 3.0 program is transpiled on riqu server.
        The QURI Parts transpiling feature is not supported.

        Args:
            qasm: The OpenQASM 3.0 program to be sampled.
            n_shots: Number of repetitions of each circuit, for sampling.
            transpiler: The transpiler setting.
            remark: The remark to be assigned to the job.

        Returns:
            The job to be executed.

        Raises:
            ValueError: If ``n_shots`` is not a positive integer.
            BackendError: If job is wrong or if an authentication error occurred, etc.
        """
        if not n_shots >= 1:
            raise ValueError("n_shots should be a positive integer.")

        try:
            body = JobsBody(
                qasm=qasm,
                shots=n_shots,
                transpiler=transpiler,
                remark=remark,
                job_type=job_type,
            )
            response_post_job = self._job_api.post_job(body=body)
            response = self._job_api.get_job(response_post_job.job_id)
        except Exception as e:
            raise BackendError("To perform sampling on riqu server is failed.") from e

        job = RiquSamplingJob(response, self._job_api)
        return job

    def retrieve_job(self, job_id: str) -> RiquSamplingJob:
        """Retrieves the job with the given id from riqu server.

        Args:
            job_id: The id of the job to retrieve.

        Returns:
            The job with the given ``job_id``.

        Raises:
            BackendError: If job cannot be found or if an authentication error occurred,
                etc.
        """
        try:
            response = self._job_api.get_job(job_id)
        except Exception as e:
            raise BackendError("To retrieve_job from riqu server is failed.") from e

        job = RiquSamplingJob(response, self._job_api)
        return job
