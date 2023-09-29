from typing import TYPE_CHECKING, NamedTuple

from quri_parts.core.estimator import Estimatable, Estimate
from quri_parts.core.operator import zero

from .sampling import RiquSamplingBackend

class _Estimate(NamedTuple):
    value: complex
    error: float = 0.0

def estimator(operator: Estimatable, state) -> Estimate[complex]:
    if operator == zero():
        return _Estimate(value=0.0)
    job = RiquSamplingBackend.sample(operator, state)
    exp = job.counts.get(0)
    return _Estimate(value=exp)
