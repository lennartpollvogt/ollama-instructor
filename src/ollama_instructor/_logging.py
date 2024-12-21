import logging
from typing import Literal

class LoggingMixin:
    """Mixin class to handle logging configuration"""
    @staticmethod
    def setup_logging(
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | int = "INFO",
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    ) -> None:
        """
        Configure logging for the ollama-instructor library.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL or logging constants)
            format: Logging format string
        """
        logger = logging.getLogger("ollama_instructor")

        # Convert string level to logging constant if necessary
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        # Create handler if none exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(format))
            logger.addHandler(handler)

        logger.setLevel(level)
