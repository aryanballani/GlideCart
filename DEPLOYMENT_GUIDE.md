# Grocery Buddy - Deployment Guide

## 🚀 Quick Start

### Raspberry Pi Setup

1. **Deploy code to Raspberry Pi:**
   ```bash
   ./deploy_to_pi.sh
   ```

2. **Start the robot server on Pi:**
   ```bash
   ssh ishman@10.19.129.238
   cd /home/ishman/grocery-buddy
   python3 main_server.py
   ```

3. **Run Android app:**
   - Open `android-app` in Android Studio
   - Build and run on your device
   - The app will automatically connect to `10.19.129.238:8765`

---

## 📋 Detailed Setup Instructions

### Prerequisites

**Raspberry Pi:**
- Python 3.7+
- Camera connected and enabled
- Dependencies: `websockets`, `opencv-python`, `numpy`

**Android Device:**
- Android Studio installed on development machine
- Android device or emulator
- Same network as Raspberry Pi

### Raspberry Pi Installation

#### Option 1: Automatic Deployment (Recommended)

```bash
# From your laptop
cd /home/kanish10/Desktop/NWHacks
./deploy_to_pi.sh
```

This script will:
- Copy all files to the Pi
- Install dependencies
- Set up the project directory

#### Option 2: Manual Deployment

```bash
# SSH into Pi
ssh ishman@10.19.129.238

# Create directory
mkdir -p ~/grocery-buddy

# Exit SSH
exit

# Copy files from your laptop
rsync -avz raspberry-pi/ ishman@10.19.129.238:~/grocery-buddy/

# SSH back in
ssh ishman@10.19.129.238

# Install dependencies
cd ~/grocery-buddy
pip3 install --user websockets opencv-python numpy
```

### Running the Robot Server

#### Interactive Mode (recommended for testing):

```bash
ssh ishman@10.19.129.238
cd /home/ishman/grocery-buddy
python3 main_server.py
```

You'll see output like:
```
======================================================================
GROCERY BUDDY - WebSocket Server Mode
======================================================================

✅ RobotController initialized
📷 Camera mode: SCAN
🎯 Target distance: 1.0m

🌐 Starting WebSocket server on 0.0.0.0:8765
📱 Connect your Android app to this Pi's IP address
⚠️  Press Ctrl+C to stop
```

#### Background Mode:

```bash
ssh ishman@10.19.129.238 'cd /home/ishman/grocery-buddy && nohup python3 main_server.py > robot.log 2>&1 &'
```

Check logs:
```bash
ssh ishman@10.19.129.238 'tail -f /home/ishman/grocery-buddy/robot.log'
```

Stop background server:
```bash
ssh ishman@10.19.129.238 'pkill -f main_server.py'
```

---

## 📱 Android App Setup

### Building the App

1. **Open in Android Studio:**
   ```bash
   cd /home/kanish10/Desktop/NWHacks/android-app
   # Open this directory in Android Studio
   ```

2. **Sync Gradle:**
   - Android Studio will automatically sync
   - Wait for build to complete

3. **Run on Device:**
   - Connect Android device via USB or use emulator
   - Click Run (▶️) button
   - Select your device

### Configuring Pi IP Address

The app defaults to `10.19.129.238:8765`. To change:

1. Open the app
2. Tap Settings icon (⚙️) in top bar
3. Enter new IP address
4. Tap "Save & Reconnect"

---

## 🎮 Using the App

### Features

**Mode Toggle:**
- **SCAN Mode**: Detects and identifies grocery items
- **FOLLOW Mode**: Tracks person with ArUco marker

**Control Buttons:**
- **CALIBRATE**: Calibrate person tracking (FOLLOW mode only)
- **START/STOP**: Enable/disable robot tracking
- **EMERGENCY STOP**: Immediately stop all motors

**Additional Features:**
- ✅ Live camera feed toggle (video icon)
- ✅ Connection status indicator
- ✅ Auto-strike detected items
- ✅ Add items manually
- ✅ Delete confirmation dialog

### Workflow

#### Grocery Scanning Workflow:

1. **Add items to your list:**
   - Tap the "+" button
   - Enter item name and quantity
   - Tap "Add"

2. **Switch to SCAN mode:**
   - Tap "SCAN" in the mode toggle

3. **Start tracking:**
   - Ensure robot is connected (WiFi icon green)
   - Tap "START"

4. **Scan items:**
   - Point camera at grocery items
   - Detected items will automatically be struck off
   - Items not on list will be added and struck off

#### Person Following Workflow:

1. **Switch to FOLLOW mode:**
   - Tap "FOLLOW" in the mode toggle

2. **Calibrate marker:**
   - Hold ArUco marker in center of camera view
   - Tap "CALIBRATE"
   - Wait for success message

3. **Start following:**
   - Tap "START"
   - Robot will follow the ArUco marker
   - Maintains ~1 meter distance

---

## 🔧 Troubleshooting

### Connection Issues

**Problem:** App shows "Disconnected" or "Error"

**Solutions:**
1. Check Raspberry Pi is on same network
2. Verify Pi IP address in settings
3. Ensure server is running on Pi:
   ```bash
   ssh ishman@10.19.129.238 'pgrep -f main_server.py'
   ```
4. Check firewall allows port 8765

### Camera Issues

**Problem:** No video feed or detection

**Solutions:**
1. Verify camera is connected to Pi
2. Check camera is enabled:
   ```bash
   ssh ishman@10.19.129.238 'vcgencmd get_camera'
   ```
3. Test camera directly:
   ```bash
   ssh ishman@10.19.129.238
   cd /home/ishman/grocery-buddy
   python3 test_vision.py
   ```

### Emergency Stop Active

**Problem:** Robot won't move even after pressing START

**Solution:**
- Emergency stop disables all movement
- Press START or CALIBRATE to clear emergency stop
- Or reconnect the app

### Build Errors (Android)

**Problem:** Gradle sync or build fails

**Solutions:**
1. Clean and rebuild:
   - Build → Clean Project
   - Build → Rebuild Project
2. Invalidate caches:
   - File → Invalidate Caches / Restart
3. Check Android SDK installed for API level 34

---

## 🧪 Testing Without Hardware

### Test Android App (No Pi needed):

The app will run and show UI even without a Pi connection. All buttons and features can be tested except:
- Live camera feed
- Actual robot control
- Object detection

### Test Vision System (No motors):

```bash
ssh ishman@10.19.129.238
cd /home/ishman/grocery-buddy
python3 main.py  # Interactive mode with camera display
```

Press keys:
- `M` - Toggle SCAN/FOLLOW mode
- `C` - Calibrate (FOLLOW mode)
- `T` - Toggle tracking ON/OFF
- `E` - Emergency stop
- `Q` - Quit

---

## 📝 System Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│   Android App   │◄──────────────────────────►│  Raspberry Pi    │
│                 │   ws://10.19.129.238:8765  │                  │
│  - UI Controls  │                             │  - Camera        │
│  - Video Feed   │         Commands:           │  - Vision AI     │
│  - Grocery List │         • calibrate         │  - Motor Control │
│                 │         • start_tracking    │  - WebSocket     │
│                 │         • stop_tracking     │    Server        │
│                 │         • emergency_stop    │                  │
│                 │         • set_mode          │                  │
└─────────────────┘                             └──────────────────┘
         │                                               │
         │                                               │
         v                                               v
  ┌─────────────┐                              ┌──────────────────┐
  │  Supabase   │                              │  Motor Driver    │
  │  Database   │                              │  (L298N)         │
  │             │                              │                  │
  │  - Sync     │                              │  - Differential  │
  │    grocery  │                              │    Drive         │
  │    lists    │                              │  - PWM Control   │
  └─────────────┘                              └──────────────────┘
```

### Communication Protocol

**Status Updates (Pi → App, 10Hz):**
```json
{
  "type": "status",
  "tracking": true,
  "emergency_stop": false,
  "target_locked": true,
  "distance": 1.2,
  "mode": "follow",
  "calibrated": true,
  "detected_object": "Apple",
  "confidence": 0.95,
  "x_offset": 0.15,
  "y_offset": -0.05,
  "tracking_offset": 0.15,
  "battery": 100,
  "obstacle_detected": false
}
```

**Commands (App → Pi):**
```json
{"command": "calibrate"}
{"command": "start_tracking"}
{"command": "stop_tracking"}
{"command": "emergency_stop"}
{"command": "set_mode", "mode": "scan"}
```

---

## 🎯 Key Features Implemented

✅ **Mode Toggle**: Switch between SCAN and FOLLOW modes
✅ **Live Video Feed**: Real-time camera stream to app
✅ **IP Configuration**: Configure Pi IP in app settings
✅ **Confirm Delete**: Dialog before deleting items
✅ **Emergency Stop**: Immediate motor shutdown
✅ **Auto-Strike**: Detected items auto-checked off
✅ **Auto-Add**: Unknown items added and struck off
✅ **Calibration**: ArUco marker calibration for person tracking
✅ **X/Y Tracking**: Camera position tracking integrated
✅ **WebSocket Integration**: Full bidirectional communication

---

## 📦 Project Structure

```
NWHacks/
├── raspberry-pi/
│   ├── main.py                 # Interactive robot controller
│   ├── main_server.py          # WebSocket server mode
│   ├── motors/
│   │   └── motor_controller.py
│   ├── vision/
│   │   ├── camera_controller.py
│   │   ├── aruco_tracker.py
│   │   ├── object_detector.py
│   │   └── config.py
│   └── server/
│       └── websocket_server.py
├── android-app/
│   └── app/src/main/java/com/grocerybuddy/
│       ├── MainActivity.kt
│       ├── viewmodel/
│       │   └── RobotViewModel.kt
│       ├── network/
│       │   ├── RobotWebSocket.kt
│       │   └── SupabaseService.kt
│       ├── ui/
│       │   ├── screens/
│       │   │   └── HomeScreen.kt
│       │   └── components/
│       │       ├── ControlButtons.kt
│       │       ├── GroceryItemCard.kt
│       │       └── StatusCard.kt
│       └── data/
│           ├── GroceryItem.kt
│           └── GroceryDatabase.kt
├── deploy_to_pi.sh             # Deployment script
└── DEPLOYMENT_GUIDE.md         # This file
```

---

## 🐛 Known Issues

1. **Motor Control Not Tested**: Per your request, motor functionality has not been tested yet
2. **Video Quality**: May need adjustment based on network bandwidth
3. **YOLO Model**: Requires model file for full object detection (falls back to color detection)

---

## 🚨 Safety Notes

⚠️ **IMPORTANT**:
- Keep emergency stop button accessible at all times
- Test in open area away from obstacles
- Monitor battery level
- Emergency stop disables motors immediately
- Motors will NOT restart until emergency stop is cleared and START is pressed

---

## 📞 Support

For issues or questions:
1. Check logs: `ssh ishman@10.19.129.238 'tail -f /home/ishman/grocery-buddy/robot.log'`
2. Restart server: `ssh ishman@10.19.129.238 'pkill -f main_server.py && cd /home/ishman/grocery-buddy && python3 main_server.py'`
3. Check network connectivity
4. Verify camera with `test_vision.py`
