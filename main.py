"""Main orchestrator launching capture and dashboard."""
# TODO: add unit tests

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

from analytics import Analytics
from audio_capture import AudioCapture
from dashboard import Dashboard
from utils.data_io import append_csv
from video_capture import VideoCapture

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Entry point."""
    audio = AudioCapture()
    video = VideoCapture()
    analytics = Analytics()
    dashboard = Dashboard()

    threading.Thread(target=audio.run, daemon=True).start()
    threading.Thread(target=video.run, daemon=True).start()
    threading.Thread(target=dashboard.start, daemon=True).start()

    log_path = Path("logs/metrics.csv")

    while True:
        clap = audio.get_latest_clapscore()
        engage = video.get_latest_engage()
        heat = analytics.push(clap, engage)
        dashboard.push(clap, engage, heat)
        append_csv(log_path, [time.time(), clap, engage, heat])
        time.sleep(1)


if __name__ == "__main__":
    main()
