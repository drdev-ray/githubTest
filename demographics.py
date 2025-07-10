"""Age and gender estimation using ONNX model."""
# TODO: add unit tests

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
try:
    import onnxruntime as ort
    ORT_AVAILABLE = True
except Exception as exc:  # pragma: no cover - import time
    ort = None
    ORT_AVAILABLE = False
    logging.warning("onnxruntime missing, demographics disabled: %s", exc)

logger = logging.getLogger(__name__)
MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/age_gender/age_gender.onnx"
MODEL_PATH = Path("downloads/age_gender.onnx")
_session = None


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max())
    return e / e.sum()


def _ensure_model() -> None:
    if MODEL_PATH.exists():
        return
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    except Exception as exc:  # pragma: no cover - runtime only
        logger.error("Model download failed: %s", exc)
        raise


def _load_session() -> "ort.InferenceSession":
    if not ORT_AVAILABLE:
        raise RuntimeError("onnxruntime is not available")
    global _session
    if _session is None:
        _ensure_model()
        _session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    return _session


def classify(roi: np.ndarray, enabled: bool = True) -> Tuple[str, str]:
    """Return age bin and gender string."""  # TODO unit-test
    if not enabled or not ORT_AVAILABLE:
        return "unknown", "unknown"
    session = _load_session()
    img = cv2.resize(roi, (224, 224))
    img = img.astype(np.float32) / 255.0
    img = img.transpose(2, 0, 1)[None]
    gender_logits, age_logits = session.run(None, {session.get_inputs()[0].name: img})
    gender = "male" if gender_logits[0][0] > gender_logits[0][1] else "female"
    age_id = int(np.argmax(age_logits[0]))
    if age_id <= 1:
        age_bin = "teen"
    elif age_id <= 3:
        age_bin = "twenties"
    elif age_id <= 5:
        age_bin = "thirties"
    else:
        age_bin = "forties"
    return age_bin, gender
