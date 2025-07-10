"""Heat Index fusion and smoothing."""
# TODO: add unit tests

from __future__ import annotations

import logging
from queue import Queue
from typing import Tuple

from utils.smoothing import ema

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Analytics:
    """Fuse metrics into a single Heat Index."""

    def __init__(self) -> None:
        """Initialize state."""  # TODO unit-test
        self._prev_heat = 0.0
        self.queue: Queue[Tuple[float, float, float]] = Queue()

    def calc_heatindex(self, engage: float, focus: float, demo_weight: float) -> float:
        """Return smoothed Heat Index."""  # TODO unit-test
        e = max(0.0, min(engage, 100.0))
        f = max(0.0, min(focus, 100.0))
        d = max(0.0, min(demo_weight, 100.0))
        heat = 0.5 * e + 0.3 * f + 0.2 * d
        heat = ema(self._prev_heat, heat)
        self._prev_heat = heat
        return heat

    def push(self, engage: float, focus: float, demo_weight: float) -> float:
        """Compute heat and push to queue."""  # TODO unit-test
        heat = self.calc_heatindex(engage, focus, demo_weight)
        self.queue.put((engage, focus, heat))
        return heat
