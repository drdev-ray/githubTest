"""Facial engagement detection utilities."""
# TODO: add unit tests

from __future__ import annotations

import numpy as np


def eye_aspect_ratio(landmarks: np.ndarray) -> float:
    """Compute eye aspect ratio."""  # TODO unit-test
    left = np.linalg.norm(landmarks[159] - landmarks[145])
    width = np.linalg.norm(landmarks[33] - landmarks[133])
    return left / (width + 1e-6)


def smile_ratio(landmarks: np.ndarray) -> float:
    """Compute smile ratio."""  # TODO unit-test
    mouth = np.linalg.norm(landmarks[61] - landmarks[291])
    face = np.linalg.norm(landmarks[1] - landmarks[199])
    return mouth / (face + 1e-6)


def calculate(landmarks: np.ndarray) -> bool:
    """Return True if face appears positive and attentive."""  # TODO unit-test
    eye_open = eye_aspect_ratio(landmarks) > 0.2
    smiling = smile_ratio(landmarks) > 0.35
    return eye_open and smiling
