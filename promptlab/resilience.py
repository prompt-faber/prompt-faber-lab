from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

import pybreaker
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential_jitter

T = TypeVar("T")


@dataclass(frozen=True)
class ResiliencePolicy:
    retries: int = 3
    breaker_fail_max: int = 5
    breaker_reset_timeout_s: int = 30


class ResilienceError(RuntimeError):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


def call_with_resilience(fn: Callable[[], T], policy: ResiliencePolicy) -> T:
    breaker = pybreaker.CircuitBreaker(
        fail_max=policy.breaker_fail_max,
        reset_timeout=policy.breaker_reset_timeout_s,
    )

    @retry(
        reraise=True,
        stop=stop_after_attempt(policy.retries),
        wait=wait_exponential_jitter(initial=0.2, max=3.0),
    )
    def _call() -> T:
        return breaker.call(fn)

    try:
        return _call()
    except RetryError as exc:
        raise ResilienceError("Falha após tentativas de retry.", cause=exc) from exc
    except pybreaker.CircuitBreakerError as exc:
        raise ResilienceError("Circuit breaker aberto; operação bloqueada temporariamente.", cause=exc) from exc
