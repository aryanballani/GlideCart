# Grocery Buddy - Raspberry Pi

Python-based robot control system with computer vision tracking.

## Features

- **Color-based tracking** using OpenCV
- **Motor control** via pigpio for smooth PWM
- **WebSocket server** for Android app communication
- **Ultrasonic sensor** for obstacle detection
- **Autonomous following** with distance maintenance

## Requirements

### Hardware
- Raspberry Pi 4/5 (4GB+ RAM recommended)
- Pi Camera v2 or USB Camera
- L298N Motor Driver
- 2x DC Motors (6-12V)
- HC-SR04 Ultrasonic Sensor
- Power supplies (for Pi and motors)

### Software
- Python 3.9+
- OpenCV
- pigpio
- websockets
- asyncio

## Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-opencv python3-numpy \
    python3-picamera2 libatlas-base-dev

# Install Python packages
pip3 install flask flask-cors websockets asyncio RPi.GPIO pigpio

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Enable hardware PWM
sudo pigpiod
```

## Project Structure

```
raspberry-pi/
├── main.py                 # Main entry point
├── config.py              # Configuration and pin definitions
├── requirements.txt       # Python dependencies
├── tracking/
│   ├── __init__.py
│   ├── color_tracker.py   # OpenCV color tracking
│   └── qr_tracker.py      # QR code tracking (optional)
├── motors/
│   ├── __init__.py
│   └── motor_controller.py # Motor control via pigpio
├── sensors/
│   ├── __init__.py
│   └── ultrasonic.py      # Distance sensor
└── server/
    ├── __init__.py
    └── websocket_server.py # WebSocket communication
```

## Configuration

Edit `config.py` to customize:
- GPIO pin assignments
- Target color HSV range
- Following distance
- Motor speeds
- Camera settings

## Running

```bash
# Start pigpio daemon (required for PWM)
sudo pigpiod

# Run the robot
python3 main.py
```

The WebSocket server will start on port 8765.

## Calibration

1. Start the robot
2. Position the colored marker in front of the camera
3. Press CALIBRATE in the Android app
4. The robot will lock onto the marker color

## Color Marker Setup

Use a bright neon marker (15cm x 15cm minimum):
- **Pink/Magenta** (recommended) - HSV: (140-170, 100-255, 100-255)
- **Neon Green** - HSV: (35-85, 100-255, 100-255)
- **Neon Orange** - HSV: (5-25, 150-255, 150-255)

## Troubleshooting

### Motors not spinning
- Check L298N ENA/ENB jumpers
- Verify GPIO pin connections
- Check motor power supply voltage

### Camera not found
- Run `vcgencmd get_camera`
- Check ribbon cable connection
- Try `sudo raspi-config` to enable camera

### Poor tracking
- Adjust HSV color range in config.py
- Increase marker size
- Improve lighting conditions

### WebSocket disconnects
- Check WiFi signal strength
- Use static IP or `raspberrypi.local`
- Verify firewall settings

## API Commands

The WebSocket server accepts JSON commands:

```json
{"command": "calibrate"}
{"command": "start_tracking"}
{"command": "stop_tracking"}
{"command": "emergency_stop"}
{"command": "get_status"}
```

Status responses include:
- `tracking`: bool
- `target_locked`: bool
- `distance`: float (meters)
- `battery`: int (percentage)
- `obstacle_detected`: bool
