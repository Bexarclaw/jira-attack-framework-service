"""Retry logic with exponential backoff.

This module provides decorators and utilities for retrying
failed operations with exponential backoff.
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import httpx

from src.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def exponential_backoff(
    attempt: int,
    base_delay: float = 2.0,
    max_delay: float = 16.0,
) -> float:
    """Calculate exponential backoff delay.

    Args:
        attempt: Attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2**attempt), max_delay)
    return delay


def with_retry(
    max_attempts: int = 4,
    base_delay: float = 2.0,
    max_delay: float = 16.0,
    exceptions: tuple[type[Exception], ...] = (
        httpx.HTTPError,
        httpx.NetworkError,
        httpx.TimeoutException,
    ),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry function calls with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exception types to retry on

    Returns:
        Decorator function

    Example:
        @with_retry(max_attempts=3)
        def fetch_data():
            return requests.get("https://api.example.com")
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        delay = exponential_backoff(attempt, base_delay, max_delay)

                        logger.warning(
                            "retry_attempt",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_attempts=max_attempts,
                            delay=delay,
                            error=str(e),
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            "retry_exhausted",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e),
                        )

            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError(f"Function {func.__name__} failed after {max_attempts} attempts")

        return wrapper

    return decorator


class RetryContext:
    """Context manager for retry logic.

    Example:
        with RetryContext(max_attempts=3) as retry:
            for attempt in retry:
                try:
                    result = some_operation()
                    break
                except Exception as e:
                    if not retry.should_retry(e):
                        raise
    """

    def __init__(
        self,
        max_attempts: int = 4,
        base_delay: float = 2.0,
        max_delay: float = 16.0,
        exceptions: tuple[type[Exception], ...] = (httpx.HTTPError,),
    ) -> None:
        """Initialize retry context.

        Args:
            max_attempts: Maximum number of attempts
            base_delay: Base delay between retries
            max_delay: Maximum delay between retries
            exceptions: Exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions
        self.current_attempt = 0

    def __enter__(self) -> "RetryContext":
        """Enter context."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        pass

    def __iter__(self) -> "RetryContext":
        """Iterate over attempts."""
        return self

    def __next__(self) -> int:
        """Get next attempt number."""
        if self.current_attempt >= self.max_attempts:
            raise StopIteration

        attempt = self.current_attempt
        self.current_attempt += 1
        return attempt

    def should_retry(self, exception: Exception) -> bool:
        """Check if should retry after exception.

        Args:
            exception: Exception that occurred

        Returns:
            True if should retry, False otherwise
        """
        if not isinstance(exception, self.exceptions):
            return False

        if self.current_attempt >= self.max_attempts:
            return False

        # Calculate and apply delay
        delay = exponential_backoff(
            self.current_attempt - 1,
            self.base_delay,
            self.max_delay,
        )

        logger.warning(
            "retry_context_delay",
            attempt=self.current_attempt,
            max_attempts=self.max_attempts,
            delay=delay,
        )

        time.sleep(delay)
        return True
