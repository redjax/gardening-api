from __future__ import annotations

import stackprinter

stackprinter.set_excepthook(style="darkbg2")

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
    base_params,
    plants_url,
    genus_url,
    build_url,
)

import trio
import httpx
from pathlib import Path

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)
print(f"Settings: {trefle_api_settings}")

from util.validators import valid_req_libs


async def make_req(url: str = None, params: dict[str, Any] = None) -> dict[str, Any]:
    # log.debug(f"Requesting URL {url}")
    async with httpx.AsyncClient(params=params) as client:
        # res = await client.get(url=url)
        request = client.build_request("GET", url)
        res = await client.send(request)

    return res.json()


async def multirequest_plants(req_list: list = None):
    ## Don't set params in this httpx AsyncClient.
    #  The params change in the for loop
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
    async with trio.open_nursery() as nursery:
        log.debug(f"Genus URL: {genus_url}")
        log.debug(f"Plants URL: {plants_url}")

        with benchmark("Request All Genus"):
            try:
                all_genus = await make_req(genus_url, params=base_params)
            except trio.Cancelled as exc:
                log.error(
                    {
                        "exception": "trio.Cancelled",
                        "details": {"msg": exc},
                        "extra": {"url": genus_url},
                    }
                )

        with benchmark("Request All Plants"):
            try:
                all_plants = await make_req(plants_url, params=base_params)
            except trio.Cancelled as exc:
                log.error(
                    {
                        "exception": "trio.Cancelled",
                        "details": {"msg": exc},
                        "extra": {"url": plants_url},
                    }
                )

        log.debug(f"All Genus ({type(all_genus)}):\n{all_genus}")
        log.debug(f"All Plants ({type(all_plants)}):\n{all_plants}")

        plant_search_base_url = f"{plants_url}/search"
        log.debug(f"Plant search base URL: {plant_search_base_url}")
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
