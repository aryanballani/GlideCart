"""
Fall Detector - Heuristic fall detection using person bounding boxes.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import time

import cv2

from .config import (
    FALL_ASPECT_RATIO_THRESHOLD,
    FALL_VERTICAL_SPEED_THRESHOLD_PX,
    FALL_CONSECUTIVE_FRAMES,
    FALL_DEBUG_LOG,
    FALL_DEBUG_LOG_INTERVAL_S,
)


@dataclass
class FallDetection:
    """Result of fall detection."""
    found: bool
    fall_detected: bool = False
    bbox: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
    aspect_ratio: float = 0.0
    vertical_speed_px_s: float = 0.0
    reason: str = ""


class FallDetector:
    """Detects falls using a lightweight person detector + heuristics."""

    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self._prev_center_y: Optional[float] = None
        self._prev_time: Optional[float] = None
        self._fall_frames = 0
        self._last_log_time: float = 0.0

    def _detect_person(self, frame) -> Optional[Tuple[int, int, int, int]]:
        boxes, _ = self.hog.detectMultiScale(
            frame,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
        )
        if boxes is None or len(boxes) == 0:
            return None

        # Pick the largest detected person
        x, y, w, h = max(boxes, key=lambda b: b[2] * b[3])
        return int(x), int(y), int(w), int(h)

    def update(self, frame) -> FallDetection:
        bbox = self._detect_person(frame)
        now = time.time()

        if bbox is None:
            self._fall_frames = 0
            self._prev_center_y = None
            self._prev_time = None
            return FallDetection(found=False, reason="no_person")

        x, y, w, h = bbox
        aspect_ratio = w / h if h > 0 else 0.0

        cy = y + h / 2.0
        vertical_speed = 0.0
        if self._prev_center_y is not None and self._prev_time is not None:
            dt = max(now - self._prev_time, 1e-3)
            vertical_speed = (cy - self._prev_center_y) / dt

        self._prev_center_y = cy
        self._prev_time = now

        fall_likely = (
            aspect_ratio > FALL_ASPECT_RATIO_THRESHOLD
            or vertical_speed > FALL_VERTICAL_SPEED_THRESHOLD_PX
        )

        if fall_likely:
            self._fall_frames += 1
        else:
            self._fall_frames = 0

        fall_detected = self._fall_frames >= FALL_CONSECUTIVE_FRAMES
        reason = "aspect_ratio" if aspect_ratio > FALL_ASPECT_RATIO_THRESHOLD else ""
        if vertical_speed > FALL_VERTICAL_SPEED_THRESHOLD_PX:
            reason = "vertical_speed" if not reason else f"{reason}+vertical_speed"

        if FALL_DEBUG_LOG:
            if now - self._last_log_time >= FALL_DEBUG_LOG_INTERVAL_S:
                self._last_log_time = now
                print(
                    "fall_debug "
                    f"bbox=({x},{y},{w},{h}) "
                    f"ar={aspect_ratio:.2f} "
                    f"vy={vertical_speed:.1f} "
                    f"frames={self._fall_frames} "
                    f"fall={fall_detected}"
                )

        return FallDetection(
            found=True,
            fall_detected=fall_detected,
            bbox=bbox,
            aspect_ratio=aspect_ratio,
            vertical_speed_px_s=vertical_speed,
            reason=reason,
        )
