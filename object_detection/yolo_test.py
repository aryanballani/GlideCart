from ultralytics import YOLO
import cv2
import time

# Load a YOLOv8 model (you can specify a different model if needed)
model = YOLO('yolov8n.pt')

# Open default webcam (change index if needed)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam (index 0). Try a different index like 1.")

fps_time = 0.0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run inference on the current frame
        results = model(frame)           # model(...) accepts numpy frames
        annotated_frame = results[0].plot()  # annotated BGR numpy image

        # Draw FPS on the frame
        now = time.time()
        fps = 1.0 / (now - fps_time) if fps_time else 0.0
        fps_time = now
        cv2.putText(annotated_frame, f'FPS: {fps:.1f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        cv2.imshow('YOLOv8 Webcam', annotated_frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()