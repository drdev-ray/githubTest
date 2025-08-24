"""HeatIndex fusion and smoothing."""
# TODO: add unit tests

from __future__ import annotations

import logging
from queue import Queue
from typing import Tuple

from utils.smoothing import ema

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Analytics:
    """Fuse metrics into HeatIndex."""

    def __init__(self) -> None:
        """Initialize queues and state. # TODO: unit test"""
        self._prev_heat = 0.0
        self.queue: Queue[Tuple[float, float, float]] = Queue()

    def calc_heatindex(self, clap: float, engage: float) -> float:
        """Calculate smoothed HeatIndex. # TODO: unit test"""
        clap_norm = max(0.0, min(clap, 100.0))
        engage_norm = max(0.0, min(engage, 100.0))
        heat = 0.4 * clap_norm + 0.6 * engage_norm
        heat = ema(self._prev_heat, heat)
        self._prev_heat = heat
        return heat

    def push(self, clap: float, engage: float) -> float:
        """Compute heat and push to queue. # TODO: unit test"""
        heat = self.calc_heatindex(clap, engage)
        self.queue.put((clap, engage, heat))
        return heat
