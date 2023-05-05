from __future__ import annotations

from core.config import app_settings, logging_settings
from core.logging.logger import get_logger

from util.time_utils import benchmark

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)
print(f"Settings: {app_settings}")

from util.validators import valid_req_libs


if __name__ == "__main__":
    ...
