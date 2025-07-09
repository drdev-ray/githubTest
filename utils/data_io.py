"""CSV append utilities."""
# TODO: add unit tests

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from retrying import retry


@retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
def append_csv(path: Path, row: Iterable) -> None:
    """Append a row to CSV, creating file if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    try:
        with path.open("a", newline="") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(["timestamp", "clap", "engage", "heat"])
            writer.writerow(row)
    except Exception as exc:  # pragma: no cover - runtime only
        raise IOError from exc
