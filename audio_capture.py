"""Audio capture and ClapScore calculation."""
# TODO: add unit tests

from __future__ import annotations

import logging
import queue
import threading
import time
from collections import deque
from typing import Deque

import numpy as np
import pyaudio
from retrying import retry

from utils.smoothing import ema

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAMES_PER_BUFFER = 1024


class AudioCapture:
    """Capture microphone input and compute ClapScore."""

    def __init__(self, display: bool = False) -> None:
        """Initialize audio resources. # TODO: unit test"""
        self._p = pyaudio.PyAudio()
        self._stream = None
        self._latest_score = 0.0
        self._lock = threading.Lock()
        self._ambient_values: Deque[float] = deque(
            maxlen=int(30 * RATE / FRAMES_PER_BUFFER)
        )
        self._clap_flags: Deque[bool] = deque(
            maxlen=int(3 * RATE / FRAMES_PER_BUFFER)
        )
        self._display = display

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
    def _open_stream(self) -> None:
        self._stream = self._p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
        )

    def get_latest_clapscore(self) -> float:
        """Thread-safe retrieval of latest ClapScore. # TODO: unit test"""
        with self._lock:
            return self._latest_score

    def _update_score(self, is_clap: bool) -> None:
        self._clap_flags.append(is_clap)
        window = list(self._clap_flags)
        score = sum(window) * (FRAMES_PER_BUFFER / RATE) * 100
        with self._lock:
            self._latest_score = score

    def run(self) -> None:
        """Main loop reading audio frames. # TODO: unit test"""
        try:
            self._open_stream()
        except Exception as exc:  # pragma: no cover - runtime only
            logger.error("Failed to open audio stream: %s", exc)
            return

        while True:
            try:
                data = self._stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
            except Exception as exc:  # pragma: no cover - runtime only
                logger.warning("Audio read error: %s", exc)
                continue

            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            rms = np.sqrt(np.mean(samples ** 2))
            rms_db = 20 * np.log10(max(rms, 1e-6))
            if self._display:
                logger.info("RMS dB: %.2f", rms_db)

            ambient_median = (
                np.median(self._ambient_values) if self._ambient_values else -60
            )
            is_clap = rms_db > ambient_median + 12

            if not is_clap:
                self._ambient_values.append(rms_db)
            self._update_score(is_clap)

            time.sleep(FRAMES_PER_BUFFER / RATE)


def main() -> None:
    """Launch audio capture (debug). # TODO: unit test"""
    cap = AudioCapture(display=True)
    thread = threading.Thread(target=cap.run, daemon=True)
    thread.start()
    for _ in range(10):
        logging.info("ClapScore: %.2f", cap.get_latest_clapscore())
        time.sleep(1)


if __name__ == "__main__":
    main()
