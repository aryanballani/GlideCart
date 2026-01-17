# Grocery Buddy - Complete Setup Guide

## Overview

This guide walks you through setting up the complete Grocery Buddy system.

## Prerequisites

### Hardware
- Raspberry Pi 4/5 (4GB+ RAM)
- Pi Camera v2 or USB webcam
- L298N Motor Driver
- 2x DC Motors (6-12V, 200RPM)
- Robot chassis (2WD or 4WD)
- HC-SR04 Ultrasonic Sensor
- Power bank (10000mAh+) for Pi
- LiPo battery (11.1V 3S) for motors
- Colored marker (15cm x 15cm, neon pink/green)
- Jumper wires, breadboard
- Android device (Android 8.0+)

### Software
- Raspberry Pi OS (64-bit recommended)
- Android Studio (for building the app)
- Python 3.9+
- Git

## Part 1: Android App Setup

### 1.1 Clone Repository

```bash
git clone https://github.com/aryanballani/nwhacks2026.git
cd nwhacks2026
```

### 1.2 Open in Android Studio

1. Launch Android Studio
2. Select "Open an Existing Project"
3. Navigate to `android-app` directory
4. Wait for Gradle sync to complete

### 1.3 Configure WebSocket URL

Edit `android-app/app/src/main/java/com/grocerybuddy/network/RobotWebSocket.kt`:

```kotlin
private val serverUrl = "ws://YOUR_PI_IP_ADDRESS:8765"
// Example: "ws://192.168.1.100:8765"
```

### 1.4 Build and Install

1. Connect your Android device via USB
2. Enable Developer Options and USB Debugging on the device
3. Click "Run" in Android Studio
4. Select your device from the deployment target

## Part 2: Raspberry Pi Setup

### 2.1 Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-opencv python3-numpy \
    python3-picamera2 libatlas-base-dev git

# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable → Reboot
```

### 2.2 Clone and Install

```bash
cd ~
git clone https://github.com/aryanballani/nwhacks2026.git
cd nwhacks2026/raspberry-pi

# Install Python packages
pip3 install -r requirements.txt

# Enable pigpio daemon (for PWM motor control)
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

### 2.3 Configure GPIO Pins

Edit `raspberry-pi/config.py` to match your wiring:

```python
# Motor pins
MOTOR_LEFT_IN1 = 17
MOTOR_LEFT_IN2 = 18
# ... adjust as needed
```

### 2.4 Find Pi IP Address

```bash
hostname -I
# Note the first IP address (e.g., 192.168.1.100)
```

## Part 3: Hardware Assembly

### 3.1 Wiring Diagram

```
Raspberry Pi GPIO → L298N Motor Driver
GPIO 17 → IN1 (Left motor forward)
GPIO 18 → IN2 (Left motor backward)
GPIO 22 → IN3 (Right motor forward)
GPIO 23 → IN4 (Right motor backward)
GPIO 12 (PWM) → ENA (Left motor enable)
GPIO 13 (PWM) → ENB (Right motor enable)
GND → GND

L298N → Motors
OUT1/OUT2 → Left Motor
OUT3/OUT4 → Right Motor
12V → Battery positive
GND → Battery negative

Ultrasonic Sensor → Raspberry Pi
VCC → 5V (Pin 2)
TRIG → GPIO 24
ECHO → GPIO 25 (via voltage divider: 1kΩ + 2kΩ)
GND → GND
```

### 3.2 Assembly Steps

1. **Mount components on chassis**
   - Secure Raspberry Pi
   - Mount L298N motor driver
   - Attach camera to front
   - Position ultrasonic sensor

2. **Connect motors**
   - Attach motors to chassis
   - Connect motor wires to L298N outputs
   - Ensure correct polarity

3. **Wire electronics**
   - Follow wiring diagram above
   - Use jumper wires and breadboard
   - Double-check all connections

4. **Power setup**
   - Connect power bank to Raspberry Pi
   - Connect LiPo battery to L298N 12V input
   - Ensure common ground

## Part 4: Testing

### 4.1 Test Camera

```bash
libcamera-hello
# Should display camera preview
```

### 4.2 Test Motors (manually)

```bash
cd ~/nwhacks2026/raspberry-pi
python3 -c "
from motors.motor_controller import MotorController
import time
motors = MotorController()
motors.forward(50)
time.sleep(2)
motors.stop()
motors.cleanup()
"
```

### 4.3 Run Full System

```bash
cd ~/nwhacks2026/raspberry-pi
sudo pigpiod  # If not already running
python3 main.py
```

### 4.4 Test Android App

1. Open the Android app
2. Check connection indicator (should turn green)
3. Test calibration and tracking buttons

## Part 5: Calibration

### 5.1 Prepare Marker

- Use bright neon marker (pink, green, or orange)
- Minimum size: 15cm x 15cm
- Attach to user's back or wheelchair

### 5.2 Calibrate Color

1. Start the robot: `python3 main.py`
2. Open Android app
3. Position marker in center of camera view
4. Press "CALIBRATE" button
5. Status should show "TARGET LOCKED"

### 5.3 Tune Following

Edit `raspberry-pi/config.py`:

```python
FOLLOW_DISTANCE = 1.0  # Adjust target distance
FOLLOW_TOLERANCE = 0.2  # Adjust tolerance
MAX_SPEED = 100  # Adjust max speed
```

## Troubleshooting

### Camera not working
```bash
# Check camera connection
vcgencmd get_camera

# Should show: supported=1 detected=1
```

### Motors not spinning
- Check L298N jumpers on ENA/ENB
- Verify battery voltage (should be 11-12V)
- Test GPIO pins with LED

### Poor tracking
- Increase marker size
- Adjust HSV range in config.py
- Improve lighting

### WebSocket connection fails
- Check Pi IP address
- Verify firewall: `sudo ufw allow 8765`
- Ensure both devices on same network

### Robot drifts/doesn't go straight
- Calibrate motor speeds
- Check wheel alignment
- Adjust left/right motor speeds independently

## Next Steps

1. Practice in a controlled environment
2. Test emergency stop functionality
3. Adjust following parameters for smooth operation
4. Prepare demo scenario
5. Have fun at the hackathon!

## Safety Notes

- Always test in a safe, open area
- Keep emergency stop accessible
- Monitor battery levels
- Supervise autonomous operation
- Have manual override ready

## Support

See complete implementation code in `claude.md`.
For issues, check the README files in each directory.
