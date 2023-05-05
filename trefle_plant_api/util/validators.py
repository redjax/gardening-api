from __future__ import annotations

from typing import Union

from core.config import logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

valid_req_libs = ["requests", "requests-cache", "httpx"]
