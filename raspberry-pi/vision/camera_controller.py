"""
Camera Controller - Main coordinator for dual-mode vision system
Switches between FOLLOW mode (person tracking) and SCAN mode (object detection)
"""

import cv2
import numpy as np
from enum import Enum
from typing import Optional, Tuple, Union
from dataclasses import dataclass

from .aruco_tracker import ArucoTracker, ArucoDetection
from .fall_detector import FallDetector
from .object_detector import ObjectDetector, ObjectDetection
from .config import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS, FALL_DETECTION_ENABLED, FALL_DEBUG_DRAW


class CameraMode(Enum):
    """Camera operating modes"""
    FOLLOW = "follow"  # Track person with colored marker
    SCAN = "scan"      # Detect and identify grocery items


@dataclass
class VisionResult:
    """Unified result from vision system"""
    mode: CameraMode
    found: bool
    label: str
    confidence: float
    center: Optional[Tuple[int, int]] = None
    bbox: Optional[Tuple[int, int, int, int]] = None
    distance: float = 0.0
    tracking_offset: float = 0.0  # -1 (left) to 1 (right) for robot steering
    raw_detection: Union[ArucoDetection, ObjectDetection, None] = None
    fall_detected: bool = False
    fall_reason: str = ""
    fall_bbox: Optional[Tuple[int, int, int, int]] = None


class CameraController:
    """
    Main vision system controller
    Manages camera, person tracking, and object detection
    """

    def __init__(self, camera_id: int = 0, use_yolo: bool = True):
        """
        Initialize camera controller

        Args:
            camera_id: Camera device ID (0 for laptop webcam, 0 for Pi)
            use_yolo: Use YOLO for object detection (fallback to color if unavailable)
        """
        self.camera_id = camera_id
        self.mode = CameraMode.SCAN  # Default mode

        # Initialize camera
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {camera_id}")

        # Initialize vision modules
        self.aruco_tracker = ArucoTracker()
        self.object_detector = ObjectDetector(use_yolo=use_yolo)
        self.fall_detector = FallDetector()
        self.fall_detection_enabled = FALL_DETECTION_ENABLED
        
        # Performance optimization - frame skipping
        self._frame_count = 0
        self._skip_frames_scan = 1  # Process every frame in SCAN mode (YOLO is optimized)
        self._skip_frames_follow = 0  # No skipping in FOLLOW mode (ArUco is fast)
        self._last_result = None  # Cache last result for skipped frames

        print(f"✓ CameraController initialized (Camera ID: {camera_id}, Mode: {self.mode.value})")

    def set_mode(self, mode: CameraMode):
        """Switch between FOLLOW and SCAN modes"""
        self.mode = mode
        print(f"✓ Mode changed to: {mode.value.upper()}")

    def calibrate_person_marker(self, frame: Optional[np.ndarray] = None) -> bool:
        """
        Calibrate person tracker to marker in center of frame

        Args:
            frame: Optional frame to use, if None will capture new frame

        Returns:
            True if calibration successful
        """
        if frame is None:
            ret, frame = self.cap.read()
            if not ret:
                return False

        return self.aruco_tracker.calibrate(frame)

    def get_follow_distance_m(self, frame: Optional[np.ndarray] = None) -> Optional[float]:
        """
        Get estimated distance (meters) to the ArUco marker.
        Returns None if no marker is detected or calibration is missing.
        """
        if frame is None:
            ret, frame = self.cap.read()
            if not ret:
                return None

        detection = self.aruco_tracker.detect(frame)
        if not detection.found:
            return None

        return detection.distance

    def process_frame(self) -> Tuple[Optional[np.ndarray], VisionResult]:
        """
        Capture and process one frame based on current mode

        Returns:
            (annotated_frame, vision_result)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, VisionResult(
                mode=self.mode,
                found=False,
                label="Camera error",
                confidence=0.0
            )

        # Determine if we should process this frame (optimization)
        skip_interval = self._skip_frames_follow if self.mode == CameraMode.FOLLOW else self._skip_frames_scan
        should_process = (self._frame_count % (skip_interval + 1)) == 0
        
        self._frame_count += 1
        
        # Process based on mode (only if not skipping or no cached result)
        if should_process or self._last_result is None:
            if self.mode == CameraMode.FOLLOW:
                result = self._process_follow_mode(frame)
            else:  # SCAN mode
                result = self._process_scan_mode(frame)
            self._last_result = result
        else:
            # Use cached result but update mode if changed
            result = self._last_result
            if result.mode != self.mode:
                # Mode changed, force reprocess
                if self.mode == CameraMode.FOLLOW:
                    result = self._process_follow_mode(frame)
                else:
                    result = self._process_scan_mode(frame)
                self._last_result = result

        # Always annotate the current frame with latest result
        annotated = self._annotate_frame(frame, result)

        return annotated, result

    def _process_follow_mode(self, frame: np.ndarray) -> VisionResult:
        """Process frame in FOLLOW mode - ArUco marker tracking"""
        detection = self.aruco_tracker.detect(frame)
        fall_detection = self.fall_detector.update(frame) if self.fall_detection_enabled else None

        if detection.found:
            # Calculate steering offset
            offset = 0.0
            if detection.center:
                offset = (detection.center[0] - CAMERA_WIDTH / 2) / (CAMERA_WIDTH / 2)

            # Distance estimation (will be 0.0 if not calibrated)
            distance_m = detection.distance if detection.distance is not None else 0.0
            
            # Determine label based on calibration status
            label = f"ArUco Marker #{detection.marker_id}" if detection.marker_id is not None else "ArUco Marker"
            if self.aruco_tracker.focal_length_px is None:
                label += " (Uncalibrated)"

            return VisionResult(
                mode=CameraMode.FOLLOW,
                found=True,
                label=label,
                confidence=detection.confidence,
                center=detection.center,
                bbox=detection.bbox,
                distance=distance_m,
                tracking_offset=offset,
                raw_detection=detection,
                fall_detected=bool(fall_detection and fall_detection.fall_detected),
                fall_reason=fall_detection.reason if fall_detection else "",
                fall_bbox=fall_detection.bbox if fall_detection else None
            )
        else:
            return VisionResult(
                mode=CameraMode.FOLLOW,
                found=False,
                label="No ArUco marker detected",
                confidence=0.0,
                raw_detection=detection,
                fall_detected=bool(fall_detection and fall_detection.fall_detected),
                fall_reason=fall_detection.reason if fall_detection else "",
                fall_bbox=fall_detection.bbox if fall_detection else None
            )

    def _process_scan_mode(self, frame: np.ndarray) -> VisionResult:
        """Process frame in SCAN mode"""
        detection = self.object_detector.get_best_detection(frame)

        if detection and detection.found:
            # Calculate offset for centering on object
            offset = 0.0
            if detection.center:
                offset = (detection.center[0] - CAMERA_WIDTH / 2) / (CAMERA_WIDTH / 2)

            return VisionResult(
                mode=CameraMode.SCAN,
                found=True,
                label=detection.label,
                confidence=detection.confidence,
                center=detection.center,
                bbox=detection.bbox,
                distance=detection.distance,
                tracking_offset=offset,
                raw_detection=detection
            )
        else:
            return VisionResult(
                mode=CameraMode.SCAN,
                found=False,
                label="No objects detected",
                confidence=0.0
            )

    def _annotate_frame(self, frame: np.ndarray, result: VisionResult) -> np.ndarray:
        """Draw annotations on frame"""
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # Mode indicator (top left)
        mode_color = (255, 0, 255) if result.mode == CameraMode.FOLLOW else (0, 255, 0)
        cv2.putText(
            annotated,
            f"MODE: {result.mode.value.upper()}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            mode_color,
            2
        )

        # Calibration status (FOLLOW mode only)
        if result.mode == CameraMode.FOLLOW:
            calibrated = self.aruco_tracker.focal_length_px is not None
            calib_text = "CALIBRATED" if calibrated else "PRESS 'C' TO CALIBRATE"
            calib_color = (0, 255, 0) if calibrated else (0, 0, 255)
            cv2.putText(
                annotated,
                calib_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                calib_color,
                1
            )

        # YOLO method indicator (SCAN mode only)
        if result.mode == CameraMode.SCAN and isinstance(result.raw_detection, ObjectDetection):
            method_text = f"Method: {result.raw_detection.method.upper()}"
            cv2.putText(
                annotated,
                method_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        # Center crosshair
        cv2.line(annotated, (w//2-20, h//2), (w//2+20, h//2), (255, 255, 255), 1)
        cv2.line(annotated, (w//2, h//2-20), (w//2, h//2+20), (255, 255, 255), 1)

        # Fall detection overlay
        if result.fall_bbox and (result.fall_detected or FALL_DEBUG_DRAW):
            fx, fy, fw, fh = result.fall_bbox
            box_color = (0, 0, 255) if result.fall_detected else (255, 255, 0)
            cv2.rectangle(annotated, (fx, fy), (fx + fw, fy + fh), box_color, 2)

            if result.fall_detected:
                fall_text = "FALL DETECTED"
                cv2.putText(
                    annotated,
                    fall_text,
                    (10, h - 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

        # Detection visualization
        if result.found and result.bbox:
            x, y, bw, bh = result.bbox

            # Bounding box - GREEN for good detection, ORANGE for low confidence
            box_color = (0, 255, 0) if result.confidence > 0.5 else (0, 165, 255)
            # Draw thicker box for better visibility
            cv2.rectangle(annotated, (x, y), (x+bw, y+bh), box_color, 3)

            # Center point - RED DOT (very visible)
            if result.center:
                # Draw outer circle for better visibility
                cv2.circle(annotated, result.center, 10, (0, 0, 0), 2)  # Black outline
                cv2.circle(annotated, result.center, 8, (0, 0, 255), -1)  # Red filled

            # Label with confidence
            label_text = f"{result.label} ({result.confidence*100:.0f}%)"
            # Add background to text for better visibility
            (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x, y - text_height - 15), (x + text_width, y - 5), (0, 0, 0), -1)
            cv2.putText(
                annotated,
                label_text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                box_color,
                2
            )

            # Distance
            dist_text = f"Dist: {result.distance:.1f}m"
            if isinstance(result.raw_detection, ArucoDetection) and result.raw_detection.distance is None:
                dist_text = "Dist: --"
            cv2.putText(
                annotated,
                dist_text,
                (x, y + bh + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

            # Locked marker center (FOLLOW mode only)
            if result.mode == CameraMode.FOLLOW:
                locked_center = self.aruco_tracker.get_locked_center(frame, normalized=True)
                if locked_center is not None:
                    coord_text = f"X: {locked_center[0]:+.2f} Y: {locked_center[1]:+.2f}"
                    cv2.putText(
                        annotated,
                        coord_text,
                        (x, y + bh + 45),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1
                    )

            # Offset indicator (for robot steering)
            offset_x = int(w/2 + result.tracking_offset * w/2)
            cv2.arrowedLine(
                annotated,
                (w//2, h - 30),
                (offset_x, h - 30),
                (0, 255, 255),
                3,
                tipLength=0.3
            )
        else:
            # No detection status
            cv2.putText(
                annotated,
                result.label,
                (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        return annotated

    def release(self):
        """Release camera resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("✓ Camera released")

    def is_opened(self) -> bool:
        """Check if camera is opened"""
        return self.cap.isOpened()
