"""Video capture and FacialEngageIdx calculation."""
# TODO: add unit tests

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Deque, Optional

import cv2
import mediapipe as mp
import numpy as np
from retrying import retry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FPS = 12
ROLLING_FRAMES = FPS * 2

mp_face = mp.solutions.face_mesh
mp_detect = mp.solutions.face_detection


def eye_aspect_ratio(landmarks: np.ndarray) -> float:
    """Compute eye openness proxy. # TODO: unit test"""
    left = np.linalg.norm(landmarks[159] - landmarks[145])
    width = np.linalg.norm(landmarks[33] - landmarks[133])
    return left / (width + 1e-6)


def smile_ratio(landmarks: np.ndarray) -> float:
    """Compute smile proxy. # TODO: unit test"""
    mouth = np.linalg.norm(landmarks[61] - landmarks[291])
    face = np.linalg.norm(landmarks[1] - landmarks[199])
    return mouth / (face + 1e-6)


class VideoCapture:
    """Capture webcam frames and compute facial engagement."""

    def __init__(self, display: bool = False) -> None:
        """Initialize video capture. # TODO: unit test"""
        self._cap = None
        self._latest_engage = 0.0
        self._lock = threading.Lock()
        self._prev_value = 0.0
        self._display = display

    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=500)
    def _open_cap(self) -> None:
        self._cap = cv2.VideoCapture(0)
        self._cap.set(cv2.CAP_PROP_FPS, FPS)

    def get_latest_engage(self) -> float:
        """Thread-safe retrieval of latest engagement. # TODO: unit test"""
        with self._lock:
            return self._latest_engage

    def _update_value(self, value: float) -> None:
        with self._lock:
            self._latest_engage = value

    def run(self) -> None:
        """Main loop capturing video frames. # TODO: unit test"""
        try:
            self._open_cap()
        except Exception as exc:  # pragma: no cover - runtime only
            logger.error("Failed to open webcam: %s", exc)
            return

        with mp_face.FaceMesh(static_image_mode=False, max_num_faces=5) as face_mesh:
            with mp_detect.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5,
            ) as detect:
                while True:
                    success, frame = self._cap.read()
                    if not success:
                        logger.warning("Frame grab failed")
                        time.sleep(1 / FPS)
                        continue
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(image)
                    engage = self._prev_value
                    if results.multi_face_landmarks:
                        faces = 0
                        positive = 0
                        for face_landmarks in results.multi_face_landmarks:
                            lm = np.array(
                                [
                                    [p.x, p.y, p.z]
                                    for p in face_landmarks.landmark
                                ]
                            )
                            if eye_aspect_ratio(lm) > 0.2 and smile_ratio(lm) > 0.35:
                                positive += 1
                            faces += 1
                        if faces > 0:
                            engage = positive / faces * 100
                    self._prev_value = engage
                    self._update_value(engage)
                    if self._display:
                        cv2.imshow("Webcam", frame)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                    time.sleep(1 / FPS)
                self._cap.release()
                if self._display:
                    cv2.destroyAllWindows()


def main() -> None:
    """Launch video capture (debug). # TODO: unit test"""
    cap = VideoCapture(display=True)
    thread = threading.Thread(target=cap.run, daemon=True)
    thread.start()
    for _ in range(10):
        logging.info("Engage: %.2f", cap.get_latest_engage())
        time.sleep(1)


if __name__ == "__main__":
    main()
