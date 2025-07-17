import os
import sys

from loguru import logger

# Read log level from environment variable
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOG_FORMAT = (
    "<green>{time:MMDD HH:mm:ss.SSSSSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "{message} | "
    "<yellow>{extra}</yellow>"
)

logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL, format=LOG_FORMAT)

__all__ = ["logger"]
