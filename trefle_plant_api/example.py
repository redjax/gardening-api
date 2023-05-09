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
    base_params,
    plants_url,
    genus_url,
    build_url,
)


import trio
from trio import TrioDeprecationWarning
import warnings

warnings.filterwarnings(action="ignore", category=TrioDeprecationWarning)

from pathlib import Path

import httpx

log = get_logger(__name__, level=logging_settings.LOG_LEVEL)
print(f"Settings: {trefle_api_settings}")


async def make_req(
    url: str = None,
    params: dict[str, Any] = None,
    send_channel: trio.MemorySendChannel = None,
) -> dict[str, Any]:
    log.debug(f"Requesting URL {url}")
    async with send_channel:
        async with httpx.AsyncClient(params=params) as client:
            # res = await client.get(url=url)
            request = client.build_request("GET", url)
            res = await client.send(request)

            # return res.json()
            await send_channel.send(res.json())


async def parse_res(receive_channel: trio.MemoryReceiveChannel = None):
    async with receive_channel:
        async for value in receive_channel:
            # log.debug(f"Receive value ({type(value)}): {value}")
            log.debug(f"Receive value [{len(value)} ({type(value)})")
            log.debug(f"Keys: {value.keys()}")
            log.debug(f"Meta: {value['meta']}")

            data = value["data"]
            meta = value["meta"]

            return_obj = {"data": data, "meta": meta}

            # log.debug(f"Return obj: {return_obj}")

            return return_obj


async def main():
    log.debug(f"Genus URL: {genus_url}\nPlants URL: {plants_url}")

    async with trio.open_nursery() as nursery:
        ## Create initial send & receive channels for messaging
        #  between functions.
        #  These channels are cloned to avoid collisions.
        send_channel, receive_channel = trio.open_memory_channel(0)

        async with send_channel, receive_channel:
            ## Start producer, send a message with res
            nursery.start_soon(make_req, plants_url, base_params, send_channel.clone())
            ## Consume producers' message
            nursery.start_soon(parse_res, receive_channel.clone())


if __name__ == "__main__":
    trio.run(main)
