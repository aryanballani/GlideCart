"""
Aruco QR person tracking using OpenCV
Tracks a printed ArUco marker on the user's back

This file has been repurposed to detect printed ArUco / fiducial markers (instead of color)
and to calibrate the camera so you can estimate distance to the marker.
"""

import time
import cv2
import numpy as np

class Tracker:
    """Detects ArUco markers, calibrates focal length, and estimates distance."""

    def __init__(self, camera_id=0, marker_length_cm=5.0,
                 aruco_dict_id=cv2.aruco.DICT_4X4_50, width=640, height=480):
        """Open camera and prepare ArUco detector.
        marker_length_cm: real-world side length of your printed marker in cm.
        """
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.frame_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.marker_length_cm = float(marker_length_cm)
        self.focal_length = None  # will be set by calibrate()
        self.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_id)
        self.aruco_params = cv2.aruco.DetectorParameters_create()

    def calibrate(self, known_distance_cm=30.0, samples=15, timeout=10.0):
        """Calibrate focal length:
        Hold the printed marker facing the camera at known_distance_cm.
        This collects `samples` frames and computes focal_length.

        Returns: focal_length (pixels) or None if calibration failed.
        """
        t0 = time.time()
        widths = []
        while len(widths) < samples and (time.time() - t0) < timeout:
            ret, frame = self.cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
            if ids is None:
                continue
            # take first detected marker
            c = corners[0].reshape((4, 2))
            # width in pixels: average of top and bottom edge lengths
            top_w = np.linalg.norm(c[0] - c[1])
            bot_w = np.linalg.norm(c[2] - c[3])
            px_w = (top_w + bot_w) / 2.0
            widths.append(px_w)
        if not widths:
            return None
        avg_px_width = float(np.mean(widths))
        # focal_length = (pixel_width * known_distance) / real_width
        self.focal_length = (avg_px_width * float(known_distance_cm)) / self.marker_length_cm
        return self.focal_length

    def track(self, draw=True):
        """
        Read a frame, detect marker and estimate distance.
        Returns: (found, x_offset_px, distance_cm, frame)
          - found: bool
          - x_offset_px: positive means marker is right of image center
          - distance_cm: estimated distance (None if not calibrated)
          - frame: annotated frame (BGR)
        """
        ret, frame = self.cap.read()
        if not ret:
            return False, None, None, None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
        if ids is None:
            if draw:
                cv2.putText(frame, "No marker", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return False, None, None, frame

        # choose first marker
        c = corners[0].reshape((4, 2))
        center = c.mean(axis=0)
        x_offset = float(center[0] - (self.frame_w / 2.0))

        # pixel width (average top & bottom)
        top_w = np.linalg.norm(c[0] - c[1])
        bot_w = np.linalg.norm(c[2] - c[3])
        px_w = (top_w + bot_w) / 2.0

        distance_cm = None
        if self.focal_length:
            # distance = (real_width * focal_length) / pixel_width
            distance_cm = (self.marker_length_cm * self.focal_length) / px_w

        if draw:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.circle(frame, (int(center[0]), int(center[1])), 4, (0, 255, 0), -1)
            cv2.line(frame, (int(self.frame_w // 2), 0), (int(self.frame_w // 2), self.frame_h), (255, 0, 0), 1)
            txt = f"dx={x_offset:.1f}px"
            if distance_cm:
                txt += f", dist={distance_cm:.1f}cm"
            cv2.putText(frame, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        return True, x_offset, distance_cm, frame

    def estimate_distance(self, pixel_width_px):
        """Estimate distance (cm) given measured marker pixel width.
        Requires prior calibration (self.focal_length).
        """
        if not self.focal_length or pixel_width_px <= 0:
            return None
        return (self.marker_length_cm * self.focal_length) / float(pixel_width_px)

    def release(self):
        """Release camera resources."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
