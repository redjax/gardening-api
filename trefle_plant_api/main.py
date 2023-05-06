from __future__ import annotations

from typing import Any, Optional, Union
from core.config import trefle_api_settings, logging_settings
from core.logging.logger import get_logger

from util.time_utils import benchmark
from util.constants import (
    trefle_base_url,
    all_plants_endpoint,
    all_genus_endpoint,
    all_species_endpoint,
    token_str,
)

import trio
import httpx
from pathlib import Path

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)
print(f"Settings: {trefle_api_settings}")

from util.validators import valid_req_libs


async def build_url(
    base: str = trefle_base_url,
    endpoint: str = None,
):
    log.debug(f"Base: {base}, endpoint: {endpoint}")

    if endpoint:
        if endpoint.startswith("/"):
            endpoint = endpoint.strip("/")

    if base:
        if base.endswith("/"):
            base = base.strip("/")

    return_url = f"{base}/{endpoint}"

    return return_url


async def make_req(url: str = None, params: dict[str, Any] = None) -> dict[str, Any]:
    # log.debug(f"Requesting URL {url}")
    async with httpx.AsyncClient() as client:
        res = await client.get(url=url, params=params)

    return res.json()


async def multirequest_plants(req_list: list = None):
    async with httpx.AsyncClient() as client:
        plant_res = []

        for item in req_list:
            log.debug(f"Item: {item}")

            _url = item["url"]
            params = item["params"]
            params["q"] = item["q"]

            with benchmark(f"Request plant {item['q']}"):
                res = await client.get(url=_url, params=params)
            plant_res.append(res.json())

    return plant_res


async def main():
    base_params = {"token": token_str}

    genus_url = await build_url(base=trefle_base_url, endpoint=all_genus_endpoint)
    plants_url = await build_url(base=trefle_base_url, endpoint=all_plants_endpoint)

    async with trio.open_nursery() as nursery:
        log.debug(f"Genus URL: {genus_url}")
        log.debug(f"Plants URL: {plants_url}")

        with benchmark("Request All Genus"):
            all_genus = await make_req(genus_url, params=base_params)
        with benchmark("Request All Plants"):
            all_plants = await make_req(plants_url, params=base_params)

        # log.debug(f"All Genus ({type(all_genus)}):\n{all_genus}")
        # log.debug(f"All Plants ({type(all_plants)}):\n{all_plants}")

        plant_search_base_url = f"{plants_url}/search"
        plants_to_search = []

        log.debug(f"Looping over [{len(all_plants['data'])}] plants.")

        for _plant in all_plants["data"]:
            log.debug(f"Plant ({type(_plant)}): {_plant}")

            plant_req = {
                "url": plant_search_base_url,
                "params": base_params,
                "q": _plant["common_name"],
            }

            plants_to_search.append(plant_req)

        with benchmark("Request multiple plants async"):
            multi_plant_res = await multirequest_plants(req_list=plants_to_search)

        log.debug(f"Multiple plant search results:\n{multi_plant_res}")
        log.debug(f"Number of plants in results: {len(multi_plant_res)}")

        return multi_plant_res


if __name__ == "__main__":
    log.info("Entering Trio async")

    with benchmark("Run main Trio function"):
        trio.run(main)

    log.info("Exited Trio async")
