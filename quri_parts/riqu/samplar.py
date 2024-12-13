from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, TypeVar

from quri_parts.circuit import ImmutableQuantumCircuit
from quri_parts.core.sampling import ConcurrentSampler, MeasurementCounts
from quri_parts.core.utils.concurrent import execute_concurrently
from quri_parts.openqasm.circuit import convert_to_qasm_str

from quri_parts.riqu.backend import RiquSamplingBackend

T_common = TypeVar("T_common")
T_individual = TypeVar("T_individual")
R = TypeVar("R")
Any = object()

if TYPE_CHECKING:
    from concurrent.futures import Executor
# RiquProperty = {"qubit_index":int, "measurement_window_index":int}
# RiquResult = {"counts":MeasurementCounts,"divided_result":None,
# "properties":Mapping[int,RiquProperty],"transpiler_info":dict,"message":str}
backend = RiquSamplingBackend()


# MeasurementCountsとSamplingCountsは等価
def _sample(circuit: ImmutableQuantumCircuit, shots: int) -> MeasurementCounts:
    qasm = convert_to_qasm_str(circuit)
    job = backend.sample_qasm(qasm, n_shots=shots)
    result = job.result().counts
    return result


def _sample_sequentially(
    _: Any, circuit_shots_tuples: Iterable[tuple[ImmutableQuantumCircuit, int]]
) -> Iterable[MeasurementCounts]:
    return [_sample(circuit, shots) for circuit, shots in circuit_shots_tuples]


def _sample_concurrently(
    circuit_shots_tuples: Iterable[tuple[ImmutableQuantumCircuit, int]],
    executor: Optional["Executor"],
    concurrency: int = 1,
) -> Iterable[MeasurementCounts]:
    return execute_concurrently(
        _sample_sequentially, None, circuit_shots_tuples, executor, concurrency
    )


def create_riqu_concurrent_sampler(
    executor: Optional["Executor"] = None, concurrency: int = 1
) -> ConcurrentSampler:
    def sampler(
        circuit_shots_tuples: Iterable[tuple[ImmutableQuantumCircuit, int]]
    ) -> Iterable[MeasurementCounts]:
        return _sample_concurrently(circuit_shots_tuples, executor, concurrency)

    return sampler
