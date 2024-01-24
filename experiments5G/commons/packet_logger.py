from experiments5G.commons.common import get_isotime
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, validator, root_validator
import queue
import threading
import os
from typing import Any, Callable, Optional
import time
import pickle

# order (lat, long) or (y,x)
# Lat = Y Long = X


class LogItem(BaseModel):
    t: float
    duration: Optional[float]
    y: float  # was lat
    x: float  # was long
    size: int  # number of bytes
    response_size: int
    cache: dict

    @validator("t")
    def val_t(cls, t):
        t = float(t)
        assert t >= 0
        return t

    # def __str__(self):
    #     return f"Packet of {format_size(self.packet_size)}, lat {self.position} duration {self.duration}s"

    class Config:
        extra = "forbid"


class PayloadItem(BaseModel):
    t: str
    y: float  # was lat
    x: float  # was long
    cache: dict
    data: Optional[str] = None

    class Config:
        extra = "forbid"


def init_queue(csv_path: Path):
    q = queue.Queue()
    fields = list(LogItem.__fields__)
    df = pd.DataFrame(columns=fields)
    df.to_csv(csv_path, mode="w", index=False)

    def process_queue():
        nonlocal q, csv_path
        while True:
            item = q.get()
            assert isinstance(item, LogItem)
            d = item.dict()
            d = {k: [v] for k, v in d.items()}
            df = pd.DataFrame(data=d, index=[0])
            df.to_csv(csv_path, mode='a', index=False, header=False)
            q.task_done()

    threading.Thread(target=process_queue).start()
    return q


LOGGER_ANSWER_OPTIONS = ["true", "same"]


class PacketLogger:
    def __init__(self,
                 name,
                 csv_path: None = None):
        self.name = name
        self.queue = None
        if csv_path is not None:
            csv_path = Path(csv_path)
            csv_path.parent.mkdir(exist_ok=True, parents=True)
            self.print(f"Logging to file {csv_path}")
            self.queue = init_queue(csv_path)
        else:
            self.print("No logging")

    def print(self, msg):
        print(f"{get_isotime()}\t[{self.name}]\t{msg}")

    def _log(self, log_item: LogItem, incoming=True):
        assert isinstance(log_item, LogItem)
        s = ("Received " if incoming else "Sent ") + str(log_item)
        self.print(s)
        if self.queue is not None:
            self.queue.put(log_item)

    def server_log(self, request_data: bytes, response_data: bytes, duration=None):
        logitem = bytes_to_logitem(request_data,
                                   response_data,
                                   duration=duration)
        self._log(logitem)
        self.print(
            f"Received request of size {len(request_data)}; duration={duration}")

    def create_request_data(self, n_bytes, position, cache) -> bytes:
        return data_to_bytes(n_bytes, position, cache)

    def client_log(self, request_data: bytes, response_data: bytes, duration=None):
        logitem = bytes_to_logitem(request_data,
                                   response_data,
                                   duration=duration)
        self._log(logitem, incoming=False)
        self.print(
            f"Sent request of size {len(request_data)}; duration={logitem.duration}; received response of size {len(response_data)}")


def data_to_bytes(n_bytes: int, position: tuple, cache: dict) -> bytes:
    random_bytes = os.urandom(n_bytes)
    y, x = position  # was lat, lon
    p = PayloadItem(t='{:=#020.6f}'.format(time.time()),
                    y=y, x=x, cache=cache)
    dumped = pickle.dumps(p.dict())
    n = n_bytes - len(dumped)
    assert n >= 0
    result = dumped + random_bytes[:n]
    assert len(result) == n_bytes
    return result


def bytes_to_logitem(request_data: bytes, response_data, duration=None) -> LogItem:
    payload = PayloadItem(**pickle.loads(request_data))
    send_time = float(payload.t)
    if duration is None:
        duration = time.time() - send_time

    return LogItem(
        t=send_time,
        duration=duration,
        y=payload.y,
        x=payload.x,
        size=len(request_data),
        cache=payload.cache,
        response_size=len(response_data)
    )
