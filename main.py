"""Main orchestrator launching capture and dashboard."""
# TODO: add unit tests

from __future__ import annotations

import argparse
import logging
import threading
import time
from pathlib import Path

from analytics import Analytics
from dashboard import Dashboard
from utils.data_io import append_csv
from video_capture import VideoCapture

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Entry point."""  # TODO unit-test
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-demographics", action="store_true", help="Disable age/gender estimation")
    args = parser.parse_args()

    video = VideoCapture(use_demo=not args.no_demographics)
    analytics = Analytics()
    dashboard = Dashboard()

    def process_loop() -> None:
        """Worker collecting metrics and logging."""
        log_path = Path("logs/metrics.csv")
        while True:
            engage = video.get_latest_engage()
            focus_val = video.get_latest_focus()
            demo = video.get_latest_demo()
            demo_weight = 100.0
            heat = analytics.push(engage, focus_val, demo_weight)
            dashboard.push(engage, focus_val, heat, demo)
            row = [
                time.time(),
                engage,
                focus_val,
                heat,
                demo["male"],
                demo["female"],
                demo["unknown"],
                demo["teen"],
                demo["twenties"],
                demo["thirties"],
                demo["forties"],
            ]
            append_csv(log_path, row)
            time.sleep(1)

    threading.Thread(target=video.run, daemon=True).start()
    threading.Thread(target=process_loop, daemon=True).start()

    # Streamlit UI runs on main thread to avoid blank screen
    dashboard.start()


if __name__ == "__main__":
    main()
