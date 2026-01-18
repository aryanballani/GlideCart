"""
WebSocket server for Android app communication
Handles commands and broadcasts robot status
"""

import asyncio
import json
import websockets
import logging
from typing import Set
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobotWebSocketServer:
    """WebSocket server for robot control"""

    def __init__(self, robot_controller):
        """Initialize server with robot controller reference"""
        self.robot = robot_controller
        self.clients: Set = set()
        self.running = False

        # Camera feed settings
        self.stream_video = False
        self.video_quality = 50  # JPEG quality 0-100

    async def handler(self, websocket):
        """Handle client connections and messages"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_id}")

        # Register client
        self.clients.add(websocket)

        try:
            # Send initial status
            await self.send_status(websocket)

            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_command(data, websocket)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {client_id}: {message}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            self.clients.discard(websocket)

    async def handle_command(self, data: dict, websocket):
        """Process commands from Android app"""
        command = data.get("command")
        logger.info(f"Received command: {command}")

        if command == "calibrate":
            # Calibrate person marker
            success = self.robot.camera.calibrate_person_marker()
            response = {
                "type": "calibration_result",
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))

        elif command == "start_tracking":
            # Enable tracking
            self.robot.tracking_enabled = True
            if self.robot.emergency_stop:
                self.robot.emergency_stop = False
            logger.info("Tracking enabled")

        elif command == "stop_tracking":
            # Disable tracking
            self.robot.tracking_enabled = False
            self.robot.motors.stop()
            logger.info("Tracking disabled")

        elif command == "emergency_stop":
            # Emergency stop - stop motors and disable tracking
            self.robot.emergency_stop = True
            self.robot.tracking_enabled = False
            self.robot.motors.stop()
            logger.warning("EMERGENCY STOP activated")

        elif command == "set_mode":
            # Switch between FOLLOW and SCAN modes
            mode_str = data.get("mode", "scan").lower()
            from vision import CameraMode
            new_mode = CameraMode.FOLLOW if mode_str == "follow" else CameraMode.SCAN
            self.robot.camera.set_mode(new_mode)
            logger.info(f"Mode changed to: {new_mode.value}")

        elif command == "get_status":
            # Send current status
            await self.send_status(websocket)

        elif command == "start_video_stream":
            # Enable video streaming
            self.stream_video = True
            logger.info("Video streaming enabled")

        elif command == "stop_video_stream":
            # Disable video streaming
            self.stream_video = False
            logger.info("Video streaming disabled")

        else:
            logger.warning(f"Unknown command: {command}")

    async def send_status(self, websocket):
        """Send current robot status to a client"""
        try:
            # Get latest vision result
            frame, result = self.robot.camera.process_frame()

            # Get normalized x, y coordinates if in follow mode
            x_offset, y_offset = 0.0, 0.0
            if result.mode.value == "follow" and result.found:
                normalized_center = self.robot.camera.aruco_tracker.get_locked_center(frame, normalized=True)
                if normalized_center:
                    x_offset, y_offset = normalized_center

            status = {
                "type": "status",
                "tracking": self.robot.tracking_enabled,
                "emergency_stop": self.robot.emergency_stop,
                "target_locked": result.found,
                "distance": round(result.distance, 2) if result.found else 0.0,
                "mode": self.robot.camera.mode.value,
                "calibrated": self.robot.camera.aruco_tracker.focal_length_px is not None,
                "detected_object": result.label if result.found and result.mode.value == "scan" else "",
                "confidence": round(result.confidence, 2) if result.found else 0.0,
                "x_offset": round(x_offset, 3),
                "y_offset": round(y_offset, 3),
                "tracking_offset": round(result.tracking_offset, 3),
                "battery": 100,  # TODO: Implement battery monitoring
                "obstacle_detected": False,  # TODO: Implement ultrasonic sensor
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send(json.dumps(status))

        except Exception as e:
            logger.error(f"Error sending status: {e}")

    async def broadcast_status(self):
        """Periodically broadcast robot status to all clients"""
        while self.running:
            if self.clients:
                # Create status message
                try:
                    frame, result = self.robot.camera.process_frame()

                    # Get normalized x, y coordinates if in follow mode
                    x_offset, y_offset = 0.0, 0.0
                    if result.mode.value == "follow" and result.found:
                        normalized_center = self.robot.camera.aruco_tracker.get_locked_center(frame, normalized=True)
                        if normalized_center:
                            x_offset, y_offset = normalized_center

                    status = {
                        "type": "status",
                        "tracking": self.robot.tracking_enabled,
                        "emergency_stop": self.robot.emergency_stop,
                        "target_locked": result.found,
                        "distance": round(result.distance, 2) if result.found else 0.0,
                        "mode": self.robot.camera.mode.value,
                        "calibrated": self.robot.camera.aruco_tracker.focal_length_px is not None,
                        "detected_object": result.label if result.found and result.mode.value == "scan" else "",
                        "confidence": round(result.confidence, 2) if result.found else 0.0,
                        "x_offset": round(x_offset, 3),
                        "y_offset": round(y_offset, 3),
                        "tracking_offset": round(result.tracking_offset, 3),
                        "battery": 100,
                        "obstacle_detected": False,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Process vision result for motor control
                    if not self.robot.emergency_stop:
                        self.robot.process_vision_result(result)

                    # Broadcast to all clients
                    message = json.dumps(status)
                    disconnected = set()

                    for client in self.clients:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.add(client)

                    # Remove disconnected clients
                    self.clients -= disconnected

                    # Send video frame if streaming enabled
                    if self.stream_video and frame is not None:
                        await self.broadcast_video_frame(frame)

                except Exception as e:
                    logger.error(f"Error in broadcast loop: {e}")

            await asyncio.sleep(0.1)  # 10Hz update rate

    async def broadcast_video_frame(self, frame):
        """Broadcast video frame to all clients"""
        import cv2
        import base64

        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.video_quality])
            frame_bytes = base64.b64encode(buffer).decode('utf-8')

            message = {
                "type": "video_frame",
                "frame": frame_bytes,
                "timestamp": datetime.now().isoformat()
            }

            # Broadcast to all clients
            disconnected = set()
            message_str = json.dumps(message)

            for client in self.clients:
                try:
                    await client.send(message_str)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Remove disconnected clients
            self.clients -= disconnected

        except Exception as e:
            logger.error(f"Error broadcasting video frame: {e}")

    async def start(self, host="0.0.0.0", port=8765):
        """Start WebSocket server"""
        self.running = True

        # Start server
        async with websockets.serve(self.handler, host, port):
            logger.info(f"WebSocket server started on {host}:{port}")

            # Start status broadcast loop
            await self.broadcast_status()

    def stop(self):
        """Stop the server"""
        self.running = False
        logger.info("WebSocket server stopped")
