"""
## Vivid

A toy webframework made by me for learning purpose
"""
import logging
from vivid.http import *
from vivid.router import *

__version__ = "1.0.0-alpha1"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H-%M-%S",
    level=logging.INFO,
)
