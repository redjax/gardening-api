from __future__ import annotations

from typing import Union

from core.config import trefle_api_settings, logging_settings
from core.logging.logger import get_logger

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)

default_req_cache_dir = ".cache"

trefle_base_url = trefle_api_settings.BASE_URL
token_str = trefle_api_settings.API_KEY

all_genus_endpoint = "/genus"
all_plants_endpoint = "/plants"
all_species_endpoint = "/species"
