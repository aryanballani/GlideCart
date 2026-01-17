"""
Ultrasonic sensor (HC-SR04) for obstacle detection
Measures distance to objects in front of robot
"""

# TODO: Implement UltrasonicSensor class
# See claude.md for complete implementation code

class UltrasonicSensor:
    """HC-SR04 ultrasonic distance sensor"""

    def __init__(self):
        """Initialize sensor GPIO pins"""
        pass

    def get_distance(self):
        """
        Measure distance to nearest object
        Returns: distance in meters, or -1 if error
        """
        pass

    def cleanup(self):
        """Cleanup GPIO resources"""
        pass
