import time
from datetime import datetime

from NotificationSender import NotificationSender


class NotificationHandler:
    def __init__(self, cat_cooldown_seconds=3600, person_cooldown_seconds=10 ):
        """
        Initialize notification handler

        Args:
            cooldown_seconds: Minimum time between notifications to avoid spam
        """
        self.cat_cooldown_seconds = cat_cooldown_seconds
        self.person_cooldown_seconds = person_cooldown_seconds
        self.last_cat_notification = 0
        self.last_person_notification = 0
        self.notification_sender = NotificationSender();

    def on_cat_detected(self, detections, frame=None):
        """
        Triggered when a cat is detected

        Args:
            detections: List of all current detections
            frame: Current frame (optional, for saving images)
        """
        current_time = time.time()

        # Check if enough time has passed since last notification
        if current_time - self.last_cat_notification < self.cat_cooldown_seconds:
            return

        # Count cats in current detections
        cat_count = len([d for d in detections if d['class_name'] == 'Cat'])

        if cat_count > 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"🐱 CAT ALERT! {cat_count} cat(s) detected at {timestamp}")

            # Here you can add your specific actions:
            # - Send email notification
            # - Send push notification
            # - Save image with timestamp
            # - Log to database
            # - Send webhook
            # - Play sound alert

            # Example actions:
            saved_image_path = self._save_detection_image(frame, f"cat_detection_{timestamp.replace(':', '-').replace(' ', '_')}.jpg")
            self.notification_sender._send_notification("Cat detected!", f"{cat_count} cat(s) spotted in the area", saved_image_path)

            # Update last notification time
            self.last_cat_notification = current_time

    def on_person_detected(self, detections, frame=None):
        """
        Triggered when a person is detected (optional - you can add person-specific actions too)

        Args:
            detections: List of all current detections
            frame: Current frame (optional)
        """
        current_time = time.time()

        if current_time - self.last_person_notification < self.person_cooldown_seconds:
            return

        person_count = len([d for d in detections if d['class_name'] == 'Person'])

        if person_count > 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"👤 Person detected: {person_count} person(s) at {timestamp}")

            # Add person-specific actions here if needed
            self.last_person_notification = current_time
            saved_image_path = self._save_detection_image(frame, f"person_detection_{timestamp.replace(':', '-').replace(' ', '_')}.jpg")
            self.notification_sender._send_notification("Person detected!", f"{person_count} person(s) spotted in the area", saved_image_path)


    def _save_detection_image(self, frame, filename):
        """
        Save frame when detection occurs

        Args:
            frame: Current frame to save
            filename: Name of the file to save
        """
        if frame is not None:
            try:
                import cv2
                import os
                filepath = os.path.join("detections", filename)
                cv2.imwrite(filepath, frame)
                print(f"Detection image saved: {filepath}")
                return  filepath
            except Exception as e:
                print(f"Failed to save image: {e}")
                return None
        return None
