from __future__ import annotations

from datetime import timedelta
import json

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# from util.log.logger import get_logger
# log = get_logger(logger="dev")
from lib.constants import default_req_cache_dir
import requests_cache


def get_req_session(
    cache_dir: str = default_req_cache_dir,
    session_name: str = "default_req_cache",
    expire_after: Union[int, timedelta] = timedelta(minutes=15),
    allowable_codes: List[int] = [200, 400],
) -> requests_cache.CachedSession:
    """Create & return a requests-cache CachedSession object for caching requests."""
    if not Path(default_req_cache_dir).exists():
        Path(default_req_cache_dir).mkdir(parents=True, exist_ok=True)

    if cache_dir:
        _cache = f"{cache_dir}/{session_name}"
    else:
        _cache = session_name

    # print(f"[DEBUG] Creating cache: {_cache}")
    # log.debug(f"Creating cache: {_cache}")

    ## Create cached request session
    session = requests_cache.CachedSession(
        cache_name=_cache,
        expire_after=expire_after,
        cache_control=True,
        allowable_codes=allowable_codes,
        stale_if_error=True,
    )

    return session
