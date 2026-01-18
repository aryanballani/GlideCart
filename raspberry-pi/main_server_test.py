#!/usr/bin/env python3
"""
Grocery Buddy - Test WebSocket Server (No Camera Required)
Use this for testing Android app without camera hardware
"""

import sys
import asyncio
import json
import websockets
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockRobotController:
    """Mock robot controller for testing without hardware"""

    def __init__(self):
        self.tracking_enabled = False
        self.emergency_stop = False
        self.mode = "scan"
        self.calibrated = False
        self.target_found = False
        self.distance = 0.0
        self.detected_object = ""

        logger.info("✅ Mock RobotController initialized (TEST MODE - No Camera)")

    def shutdown(self):
        logger.info("✅ Mock shutdown complete")


class TestWebSocketServer:
    """WebSocket server for testing Android app"""

    def __init__(self, robot_controller):
        self.robot = robot_controller
        self.clients = set()
        self.running = False
        self.stream_video = False

    async def handler(self, websocket, path):
        """Handle client connections and messages"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"📱 Client connected: {client_id}")

        self.clients.add(websocket)

        try:
            await self.send_status(websocket)

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
        logger.info(f"📨 Received command: {command}")

        if command == "calibrate":
            self.robot.calibrated = True
            response = {
                "type": "calibration_result",
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))
            logger.info("✅ Calibration simulated")

        elif command == "start_tracking":
            self.robot.tracking_enabled = True
            if self.robot.emergency_stop:
                self.robot.emergency_stop = False
            logger.info("▶️  Tracking enabled")

        elif command == "stop_tracking":
            self.robot.tracking_enabled = False
            logger.info("⏸️  Tracking disabled")

        elif command == "emergency_stop":
            self.robot.emergency_stop = True
            self.robot.tracking_enabled = False
            logger.warning("🚨 EMERGENCY STOP activated")

        elif command == "set_mode":
            mode_str = data.get("mode", "scan").lower()
            self.robot.mode = mode_str
            logger.info(f"🔄 Mode changed to: {mode_str}")

        elif command == "get_status":
            await self.send_status(websocket)

        elif command == "start_video_stream":
            self.stream_video = True
            logger.info("📹 Video streaming enabled (mock)")

        elif command == "stop_video_stream":
            self.stream_video = False
            logger.info("📹 Video streaming disabled")

        else:
            logger.warning(f"❓ Unknown command: {command}")

    async def send_status(self, websocket):
        """Send current robot status to a client"""
        try:
            # Simulate some detection occasionally
            import random
            if self.robot.tracking_enabled and random.random() > 0.7:
                self.robot.target_found = True
                self.robot.distance = round(random.uniform(0.5, 2.0), 2)
                if self.robot.mode == "scan":
                    items = ["Apple", "Banana", "Milk", "Bread", ""]
                    self.robot.detected_object = random.choice(items)
            else:
                self.robot.target_found = False
                self.robot.detected_object = ""

            status = {
                "type": "status",
                "tracking": self.robot.tracking_enabled,
                "emergency_stop": self.robot.emergency_stop,
                "target_locked": self.robot.target_found,
                "distance": self.robot.distance,
                "mode": self.robot.mode,
                "calibrated": self.robot.calibrated,
                "detected_object": self.robot.detected_object,
                "confidence": 0.85 if self.robot.target_found else 0.0,
                "x_offset": 0.0,
                "y_offset": 0.0,
                "tracking_offset": 0.0,
                "battery": 100,
                "obstacle_detected": False,
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send(json.dumps(status))

        except Exception as e:
            logger.error(f"Error sending status: {e}")

    async def broadcast_status(self):
        """Periodically broadcast robot status to all clients"""
        while self.running:
            if self.clients:
                try:
                    # Simulate some detection
                    import random
                    if self.robot.tracking_enabled and random.random() > 0.7:
                        self.robot.target_found = True
                        self.robot.distance = round(random.uniform(0.5, 2.0), 2)
                        if self.robot.mode == "scan":
                            items = ["Apple", "Banana", "Milk", "Bread", "Eggs", ""]
                            self.robot.detected_object = random.choice(items)
                    else:
                        self.robot.target_found = False
                        self.robot.detected_object = ""

                    status = {
                        "type": "status",
                        "tracking": self.robot.tracking_enabled,
                        "emergency_stop": self.robot.emergency_stop,
                        "target_locked": self.robot.target_found,
                        "distance": self.robot.distance,
                        "mode": self.robot.mode,
                        "calibrated": self.robot.calibrated,
                        "detected_object": self.robot.detected_object,
                        "confidence": 0.85 if self.robot.target_found else 0.0,
                        "x_offset": 0.0,
                        "y_offset": 0.0,
                        "tracking_offset": 0.0,
                        "battery": 100,
                        "obstacle_detected": False,
                        "timestamp": datetime.now().isoformat()
                    }

                    message = json.dumps(status)
                    disconnected = set()

                    for client in self.clients:
                        try:
                            await client.send(message)
                        except websockets.exceptions.ConnectionClosed:
                            disconnected.add(client)

                    self.clients -= disconnected

                except Exception as e:
                    logger.error(f"Error in broadcast loop: {e}")

            await asyncio.sleep(0.5)  # 2Hz update rate for testing

    async def start(self, host="0.0.0.0", port=8765):
        """Start WebSocket server"""
        self.running = True

        async with websockets.serve(self.handler, host, port):
            logger.info(f"🌐 WebSocket server started on {host}:{port}")
            logger.info(f"📱 Connect your Android app to this Pi's IP address")
            logger.info(f"⚠️  TEST MODE - No camera, simulated data")

            await self.broadcast_status()

    def stop(self):
        """Stop the server"""
        self.running = False
        logger.info("WebSocket server stopped")


async def main_async():
    """Main async entry point"""
    print("=" * 70)
    print("GROCERY BUDDY - TEST WebSocket Server Mode")
    print("=" * 70)
    print()

    try:
        # Initialize mock robot controller
        robot = MockRobotController()

        # Initialize WebSocket server
        server = TestWebSocketServer(robot)

        print("\n🧪 Running in TEST MODE (no camera required)")
        print("   - Simulates random object detection")
        print("   - All commands work")
        print("   - Perfect for testing Android app\n")
        print("⚠️  Press Ctrl+C to stop\n")

        # Start server
        await server.start(host="0.0.0.0", port=8765)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'robot' in locals():
            robot.shutdown()


if __name__ == "__main__":
    asyncio.run(main_async())
