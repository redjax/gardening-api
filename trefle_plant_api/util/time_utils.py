from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta
import time

from time import perf_counter
from typing import Union

import arrow

def ts_today() -> arrow.Arrow:
    return arrow.now()


def ts_format(ts: arrow.Arrow = None) -> str:
    formatted_ts = ts.format("YYYY-MM-DD")

    return formatted_ts


@contextmanager
def benchmark(description: str = "Unnamed function timer") -> None:
    """Time a function call.

    Run a function with this context manager to time function execution.

    Usage:

    with benchmark("Short description here"):
        ...
    """
    start = time.time()
    yield
    elapsed = time.time() - start

    print(f"{description}: {elapsed}")
