+----------------+
|  Camera Frame  |
+----------------+
        |
        v
+----------------+
| Detect ArUco   |
| Compute x, z   |
+----------------+
        |
        v
+----------------+
| Compute speeds |
| linear/angular |
+----------------+
        |
        v
+----------------+
| Send to rasp pi motor class which send to motor driver the direction|
+----------------+