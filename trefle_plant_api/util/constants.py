from __future__ import annotations

from typing import Union

from core.config import trefle_api_settings, logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

default_req_cache_dir = ".cache"

trefle_base_url = trefle_api_settings.BASE_URL
token_str = trefle_api_settings.API_KEY

base_params = {"token": token_str}

all_genus_endpoint = "/genus"
all_plants_endpoint = "/plants"
all_species_endpoint = "/species"

## Append this object to any header object to disable caching
#  on requests that use those headers.
header_disable_cache = {"cache-control": "no-cache"}


def build_url(
    base: str = trefle_base_url,
    endpoint: str = None,
):
    """Clean inputs & build URL."""
    log.debug(f"Base: {base}, endpoint: {endpoint}")

    if endpoint:
        if endpoint.startswith("/"):
            endpoint = endpoint.strip("/")

    if base:
        if base.endswith("/"):
            base = base.strip("/")

    return_url = f"{base}/{endpoint}"

    return return_url


genus_url = build_url(base=trefle_base_url, endpoint=all_genus_endpoint)
plants_url = build_url(base=trefle_base_url, endpoint=all_plants_endpoint)
