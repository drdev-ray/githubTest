"""Webcam capture and metric computation."""
# TODO: add unit tests

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Deque, Dict, Tuple

import cv2
import mediapipe as mp
import numpy as np
from retrying import retry

import engagement
import focus
import demographics

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FPS = 12

mp_face = mp.solutions.face_mesh
mp_detect = mp.solutions.face_detection


class VideoCapture:
    """Capture webcam frames and compute metrics."""

    def __init__(self, use_demo: bool = True, display: bool = False) -> None:
        """Initialize capture."""  # TODO unit-test
        self._cap = None
        self._display = display
        self.use_demo = use_demo
        self._engage_window: Deque[float] = deque(maxlen=FPS)
        self._focus_window: Deque[float] = deque(maxlen=FPS)
        self._demo_window: Deque[Dict[str, float]] = deque(maxlen=FPS)
        self._lock = threading.Lock()

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
    def _open_cap(self) -> None:
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self._cap.set(cv2.CAP_PROP_FPS, FPS)

    def get_latest_engage(self) -> float:
        """Return current engagement."""  # TODO unit-test
        with self._lock:
            return float(np.mean(self._engage_window)) * 100 if self._engage_window else 0.0

    def get_latest_focus(self) -> float:
        """Return current focus."""  # TODO unit-test
        with self._lock:
            return float(np.mean(self._focus_window)) * 100 if self._focus_window else 0.0

    def get_latest_demo(self) -> Dict[str, float]:
        """Return demographic distribution."""  # TODO unit-test
        keys = ["male", "female", "unknown", "teen", "twenties", "thirties", "forties"]
        with self._lock:
            if not self._demo_window:
                return {k: 0.0 for k in keys}
            sums = {k: 0.0 for k in keys}
            for d in self._demo_window:
                for k in keys:
                    sums[k] += d.get(k, 0.0)
            return {k: sums[k] / len(self._demo_window) for k in keys}

    def _append_demo(self, counts: Dict[str, int], total: int) -> None:
        frac = {k: (v / total if total else 0.0) for k, v in counts.items()}
        with self._lock:
            self._demo_window.append(frac)

    def _append_metric(self, win: Deque[float], value: float) -> None:
        with self._lock:
            win.append(value)

    def run(self) -> None:
        """Capture loop."""  # TODO unit-test
        try:
            self._open_cap()
        except Exception as exc:  # pragma: no cover - runtime only
            logger.error("Failed to open webcam: %s", exc)
            return

        with mp_face.FaceMesh(static_image_mode=False, max_num_faces=5) as mesh:
            with mp_detect.FaceDetection(model_selection=0, min_detection_confidence=0.6) as detect:
                while True:
                    success, frame = self._cap.read()
                    if not success:
                        logger.warning("Frame grab failed")
                        time.sleep(1 / FPS)
                        continue
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = mesh.process(rgb)
                    engage_ratio = 0.0
                    focus_ratio = 0.0
                    demo_counts = {
                        "male": 0,
                        "female": 0,
                        "unknown": 0,
                        "teen": 0,
                        "twenties": 0,
                        "thirties": 0,
                        "forties": 0,
                    }
                    total = 0
                    if results.multi_face_landmarks:
                        for face_lm in results.multi_face_landmarks:
                            lm = np.array([[p.x, p.y, p.z] for p in face_lm.landmark])
                            pos = engagement.calculate(lm)
                            foc = focus.calculate(lm, frame.shape[1])
                            if pos:
                                engage_ratio += 1
                            if foc:
                                focus_ratio += 1
                            if self.use_demo:
                                x1 = int(np.min(lm[:, 0]) * frame.shape[1])
                                y1 = int(np.min(lm[:, 1]) * frame.shape[0])
                                x2 = int(np.max(lm[:, 0]) * frame.shape[1])
                                y2 = int(np.max(lm[:, 1]) * frame.shape[0])
                                roi = rgb[max(y1, 0) : max(y2, 0), max(x1, 0) : max(x2, 0)]
                                age_bin, gender = demographics.classify(roi, self.use_demo)
                            else:
                                age_bin, gender = "unknown", "unknown"
                            demo_counts[gender] = demo_counts.get(gender, 0) + 1
                            demo_counts[age_bin] = demo_counts.get(age_bin, 0) + 1
                            total += 1
                    if total:
                        engage_ratio /= total
                        focus_ratio /= total
                    self._append_metric(self._engage_window, engage_ratio)
                    self._append_metric(self._focus_window, focus_ratio)
                    self._append_demo(demo_counts, total)
                    if self._display:
                        cv2.imshow("Webcam", frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                    time.sleep(1 / FPS)
        if self._cap:
            self._cap.release()
        if self._display:
            cv2.destroyAllWindows()


def main() -> None:
    """Run as script."""  # TODO unit-test
    cap = VideoCapture(display=True)
    t = threading.Thread(target=cap.run, daemon=True)
    t.start()
    for _ in range(10):
        logging.info(
            "E: %.1f F: %.1f %s",
            cap.get_latest_engage(),
            cap.get_latest_focus(),
            cap.get_latest_demo(),
        )
        time.sleep(1)


if __name__ == "__main__":
    main()
