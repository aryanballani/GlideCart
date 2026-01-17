# GPIO Pin Configuration
# TODO: Configure GPIO pins based on your wiring

# Motor pins
MOTOR_LEFT_IN1 = 17
MOTOR_LEFT_IN2 = 18
MOTOR_RIGHT_IN3 = 22
MOTOR_RIGHT_IN4 = 23
MOTOR_LEFT_EN = 12   # PWM
MOTOR_RIGHT_EN = 13  # PWM

# Sensor pins
ULTRASONIC_TRIG = 24
ULTRASONIC_ECHO = 25

# Tracking Configuration
# Pink/Magenta HSV range (adjust based on your marker)
TARGET_COLOR_HSV_LOWER = (140, 100, 100)
TARGET_COLOR_HSV_UPPER = (170, 255, 255)

# Following behavior
FOLLOW_DISTANCE = 1.0  # meters
FOLLOW_TOLERANCE = 0.2  # meters

# Motor speeds (0-100)
MAX_SPEED = 100
TURN_SPEED = 70

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# WebSocket server
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 8765
