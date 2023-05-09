from __future__ import annotations

import stackprinter

stackprinter.set_excepthook(style="darkbg2")

import time

from typing import Any, Optional, Union
from core.config import trefle_api_settings, logging_settings
from core.logging.logger import get_logger

from util.time_utils import benchmark_async

from util.constants import (
    trefle_base_url,
    all_plants_endpoint,
    all_genus_endpoint,
    all_species_endpoint,
    token_str,
    default_req_cache_dir,
    header_disable_cache,
)

import trio
from trio import TrioDeprecationWarning
import warnings

warnings.filterwarnings(action="ignore", category=TrioDeprecationWarning)

import httpx_cache
from pathlib import Path

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)
print(f"Settings: {trefle_api_settings}")

from util.validators import valid_req_libs

## Global dict to store results
_results = []

_results_multi = []
plant_names = []


if not Path(default_req_cache_dir).exists():
    Path(default_req_cache_dir).mkdir(parents=True, exist_ok=True)


# _cache = httpx_cache.FileCache(cache_dir=default_req_cache_dir)
_cache = httpx_cache.DictCache()


async def build_url(
    base: str = trefle_base_url,
    endpoint: str = None,
):
    """Return an assembled request URL from passed parts."""
    log.debug(f"Base: {base}, endpoint: {endpoint}")

    if endpoint:
        if endpoint.startswith("/"):
            endpoint = endpoint.strip("/")

    if base:
        if base.endswith("/"):
            base = base.strip("/")

    return_url = f"{base}/{endpoint}"

    return return_url


async def fetch(
    url: str = None,
    params: dict[str, Any] = None,
    global_list: list = None,
    _log: bool = False,
) -> dict[str, Any]:
    async with httpx_cache.AsyncClient(cache=_cache) as client:
        log.debug(f"Requesting URL: {url}")
        res = await client.get(url, params=params)

        res_obj = {
            "url": url,
            "response": {
                "status_code": res.status_code,
                "elapsed": res.elapsed,
                "encoding": res.encoding,
                "json": res.json,
                "test": res.text,
            },
        }

        if _log:
            log.debug(res_obj)
            log.debug(f"[{res.status_code}: {url}]")

    # results.append(res_obj)
    if global_list:
        global_list.append(res_obj)

        return global_list

    else:
        return None

    # return res.json()


async def extract_names(obj: list = None) -> list:
    if not obj:
        raise ValueError("Missing input list.")

    log.debug(f"Input obj: {obj}")

    for item in obj:
        log.debug(f"Item: {item}")
        # plant_names.append()


async def main():
    base_params = {"token": token_str}

    genus_url = await build_url(base=trefle_base_url, endpoint=all_genus_endpoint)
    plants_url = await build_url(base=trefle_base_url, endpoint=all_plants_endpoint)

    log.debug(f"Genus URL: {genus_url}")
    log.debug(f"Plants URL: {plants_url}")

    # all_plants = await make_req(url=plants_url, params=base_params)

    # log.debug(f"All Plants ({type(all_plants)})")

    nursery_urls = [plants_url, genus_url]

    all_plants_start_time = time.time()
    async with trio.open_nursery() as nursery:
        for url in nursery_urls:
            nursery.start_soon(fetch, url, base_params, _results)
    all_plants_end_time = time.time() - all_plants_start_time
    log.debug(f"Nursery loop requests time: {all_plants_end_time}s")

    log.debug(f"Results: [{type(_results)}]: {_results}")
    log.debug(f"Nursery URL results: {len(_results)}")

    multi_req_plants_start = time.time()
    async with trio.open_nursery() as multi_nursery:
        multi_nursery.start_soon(extract_names, _results)
        # log.debug(f"Extracted names ({type(extracted_names)}): {extracted_names}")

    multi_req_plants_end = time.time() - multi_req_plants_start
    log.debug(f"Requesting all plants individually took {multi_req_plants_end}s")


if __name__ == "__main__":
    log.info("Entering Trio")

    trio.run(main)

    log.info("Exiting Trio")
