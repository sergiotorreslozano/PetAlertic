import cv2
import numpy as np
from ultralytics import YOLO
import time

from NotificationHandler import NotificationHandler


class PersonCatDetector:
    def __init__(self, model_path='yolo11n_ncnn_model', confidence_threshold=0.80):
        """
        Initialize the YOLOv11 person and cat detector with NCNN model

        Args:
            model_path: Path to YOLO NCNN model (e.g., 'yolo11n_ncnn_model')
            confidence_threshold: Minimum confidence for detections
        """
        print("Loading YOLOv11 NCNN model...")
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.person_class_id = 0  # Person class ID in COCO dataset
        self.cat_class_id = 15  # Cat class ID in COCO dataset
        self.target_classes = [self.person_class_id, self.cat_class_id]

        # Class names for display
        self.class_names = {
            0: 'Person',
            15: 'Cat'
        }

        # Colors for different classes (BGR format)
        self.colors = {
            0: (0, 255, 0),  # Green for persons
            15: (255, 0, 0)  # Blue for cats
        }

    def detect_objects(self, frame):
        """
        Detect persons and cats in a frame

        Args:
            frame: Input image/frame

        Returns:
            List of detection results with bounding boxes, confidence scores, and class info
        """
        # Run inference
        results = self.model(frame, verbose=False)

        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls)
                    confidence = float(box.conf)

                    # Check if detection is a target class and meets confidence threshold
                    if class_id in self.target_classes and confidence >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': self.class_names[class_id]
                        })

        return detections

    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels on frame

        Args:
            frame: Input frame
            detections: List of detection results

        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()

        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_id = detection['class_id']
            class_name = detection['class_name']

            # Get color for this class
            color = self.colors[class_id]

            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f'{class_name} {confidence:.2f}'
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10),
                          (x1 + label_size[0], y1), color, -1)
            cv2.putText(annotated_frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        return annotated_frame

    def get_detection_counts(self, detections):
        """
        Count detections by class

        Args:
            detections: List of detection results

        Returns:
            Dictionary with counts for each class
        """
        counts = {'Person': 0, 'Cat': 0}
        for detection in detections:
            counts[detection['class_name']] += 1
        return counts


def main():
    # Initialize detector with NCNN model
    detector = PersonCatDetector(
        model_path='yolo11n_ncnn_model',  # Use your exported NCNN model
        confidence_threshold=0.5
    )
    notifier = NotificationHandler(cat_cooldown_seconds=3600, person_cooldown_seconds=10)

    # Setup video capture (modify this according to your feed)
    # For webcam: cap = cv2.VideoCapture(0)
    # For RTSP stream: cap = cv2.VideoCapture('rtsp://your_stream_url')
    # For video file: cap = cv2.VideoCapture('path_to_video.mp4')
    # cap = cv2.VideoCapture('https://192.168.1.205:8080/video_feed_0')  # Change this to your feed source
    cap = cv2.VideoCapture(
        'https://10.100.0.205:8080/video_feed_0')  # this is for Wireguard

    if not cap.isOpened():
        print("Error: Could not open video source")
        return

    print("Starting person and cat detection... Press 'q' to quit")

    fps_counter = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        # Detect persons and cats
        detections = detector.detect_objects(frame)

        # Trigger notifications based on detections
        if detections:  # Only check if there are detections
            cats_detected = any(d['class_name'] == 'Cat' for d in detections)
            persons_detected = any(d['class_name'] == 'Person' for d in detections)

            if cats_detected:
                notifier.on_cat_detected(detections, frame)

            if persons_detected:
                notifier.on_person_detected(detections, frame)

        # Draw detections
        annotated_frame = detector.draw_detections(frame, detections)

        # Get detection counts
        counts = detector.get_detection_counts(detections)

        # Add detection counts to display
        cv2.putText(annotated_frame, f'Persons: {counts["Person"]} | Cats: {counts["Cat"]}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Calculate and display FPS
        fps_counter += 1
        if fps_counter % 10 == 0:
            end_time = time.time()
            fps = 10 / (end_time - start_time)
            start_time = end_time
            print(f"FPS: {fps:.1f}, Persons: {counts['Person']}, Cats: {counts['Cat']}")

        # Display frame
        cv2.imshow('Person and Cat Detection', annotated_frame)

        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Detection stopped")


if __name__ == "__main__":
    main()