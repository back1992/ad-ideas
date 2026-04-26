"""Shared logging utility to avoid duplication across modules."""

import logging


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create a configured logger with a StreamHandler.

    Args:
        name: Logger name (usually the module/class name).
        level: Logging level.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
