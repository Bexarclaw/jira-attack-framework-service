"""Structured logging configuration using structlog.

This module provides centralized logging setup with structured output,
supporting both console and JSON formats.
"""

import logging
import sys
from typing import Any

import structlog
from rich.console import Console
from rich.logging import RichHandler

from src.config import ConfigSettings

console = Console()


def setup_logging(config: ConfigSettings) -> None:
    """Configure structured logging with structlog.

    Args:
        config: Application configuration settings

    Sets up logging with:
    - Structured output (JSON or console format)
    - Timestamp formatting
    - Log level filtering
    - Exception formatting
    - Context injection
    """
    log_level = getattr(logging, config.log_level)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=config.is_development,
            )
        ]
        if config.log_format == "console"
        else [logging.StreamHandler(sys.stdout)],
    )

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if config.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding structured context to logs.

    Example:
        with LogContext(request_id="123", user="admin"):
            logger.info("processing request")
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize log context.

        Args:
            **kwargs: Key-value pairs to add to log context
        """
        self.context = kwargs

    def __enter__(self) -> "LogContext":
        """Enter context and bind variables."""
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and clear variables."""
        structlog.contextvars.clear_contextvars()


def log_function_call(logger: structlog.BoundLogger) -> Any:
    """Decorator to log function entry/exit with parameters.

    Args:
        logger: Logger instance to use

    Returns:
        Decorator function

    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug(
                "function_call",
                function=func.__name__,
                args=args,
                kwargs=kwargs,
            )
            try:
                result = func(*args, **kwargs)
                logger.debug("function_return", function=func.__name__)
                return result
            except Exception as e:
                logger.error(
                    "function_error",
                    function=func.__name__,
                    error=str(e),
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator
