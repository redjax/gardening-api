from __future__ import annotations

from typing import Union

from core.config import api_settings, logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

default_req_cache_dir = ".cache"
