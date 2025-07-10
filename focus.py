"""Focus estimation based on face yaw."""
# TODO: add unit tests

from __future__ import annotations

import math
import numpy as np

from engagement import eye_aspect_ratio


FOV_DEG = 60


def calculate(landmarks: np.ndarray, width: int) -> bool:
    """Return True if face looks toward stage."""  # TODO unit-test
    eye_open = eye_aspect_ratio(landmarks) > 0.2
    xs = landmarks[:, 0] * width
    center = xs.mean()
    dx = center - width / 2
    focal_len = width / (2 * math.tan(math.radians(FOV_DEG / 2)))
    yaw = math.degrees(math.atan2(dx, focal_len))
    return abs(yaw) <= 25 and eye_open
