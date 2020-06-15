import logging
import re
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Union, Tuple, Iterable, Generator, Dict
from typing import List

logger = logging.getLogger(__name__)


class Grounding(ABC):
    @abstractmethod
    def ground_sentence(self, sent: str) -> Dict[str, Union[str, List[str]]]:
        pass
