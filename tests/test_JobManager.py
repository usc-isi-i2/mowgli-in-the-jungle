import numpy as np
import time
import logging

import typing

from mowgli.utils.MapReduceJobManager import MapReduceJobManager

logger = logging.getLogger(__name__)


def get_pre_func():
    return {'pre_f': lambda l: np.power(l, 3)}


def submit_func(a: int, b: int, pre_f: typing.Callable) -> int:
    logger.info(f'Function a={a}, b={b}')
    arr = np.array([a])
    time.sleep(b)
    return pre_f(arr)


m = MapReduceJobManager(1)
m.start_workers(func=submit_func, pre_func=get_pre_func)

m.push_job((10,), b=10)
m.push_job((20,), b=50)

print(m.return_q.get())
print(m.return_q.get())

m.kill()