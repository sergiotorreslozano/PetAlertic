import json

class NotificationSender:
    def __init__(self, config_path='../config.json', secrets_path='../secrets.json'):
        self._load_config(config_path)
        self._load_secrets(secrets_path)
        pass

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.smtp_server = config.get("smtp_server")
            self.smtp_port = config.get("smtp_port")
            self.sender_password = config.get("sender_password")
            self.recipient_email = config.get("recipient_email")

    def _load_secrets(self, secrets_path):
        with open(secrets_path, 'r') as f:
            config = json.load(f)
            self.sender_email = config.get("sender_email")
            self.sender_password = config.get("sender_password")
            self.recipient_email = config.get("recipient_email")

    def _send_notification(self, title, message, image_path=None):
        """
        Send notification
        Args:
            title: Notification title
            message: Notification message
            image_path: Path to image file to attach (optional)
        """

        # 1. Email notification
        self._send_email(title, message, image_path)

        # 2. Push notification (using pushbullet, telegram, etc.)
        # self._send_push_notification(title, message)

        # 3. Webhook
        # self._send_webhook(title, message)

        print(f"NOTIFICATION: {title} - {message}")

    def _send_email(self, title, message, image_path=None):
        """
        Send email notification using Gmail SMTP with optional image attachment

        Args:
            title: Email subject title
            message: Email body message
            image_path: Path to image file to attach (optional)
        """

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.image import MIMEImage
            from email import encoders
            from datetime import datetime
            import os

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"[Detection Alert] {title}"

            # Email body
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            body = f"""
    Detection Alert

    Time: {timestamp}
    Alert: {title}
    Details: {message}

    This is an automated message from your detection system.
                """

            msg.attach(MIMEText(body, 'plain'))
            print(f"DEBUG: Attempting to attach image: {image_path}")

            # Attach image if provided and exists
            if image_path and os.path.exists(image_path):
                try:
                    print(f"DEBUG: Attempting to attach image: {image_path}")

                    with open(image_path, "rb") as f:
                        img_data = f.read()

                    # Use MIMEImage for better image handling
                    image = MIMEImage(img_data)

                    # Add header for attachment
                    filename = os.path.basename(image_path)
                    image.add_header('Content-Disposition', f'attachment; filename="{filename}"')

                    # Attach the image to message
                    msg.attach(image)
                    print(f"DEBUG: Image successfully attached: {filename}")

                except Exception as e:
                    print(f"ERROR: Failed to attach image {image_path}: {e}")
                    print(f"ERROR: Exception type: {type(e).__name__}")
            else:
                # Log why image is not being attached
                if image_path:
                    print(f"WARNING: Image path provided but file doesn't exist: {image_path}")
                else:
                    print("WARNING: No image path provided for attachment")

            # Connect to Gmail SMTP server
            print("DEBUG: Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.sender_email, self.sender_password)

            # Send email
            print("DEBUG: Sending email...")
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()

            attachment_info = " with image attachment" if image_path and os.path.exists(
                image_path) else ""
            print(
                f"SUCCESS: Email notification sent successfully to {self.recipient_email}{attachment_info}")

        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def _send_push_notification(self, title, message):
        """
        Example push notification method
        """
        # Implement push notification logic here
        # Could use services like Pushbullet, Telegram Bot, etc.
        pass

    def _send_webhook(self, title, message):
        """
        Example webhook method
        """
        # import requests
        # requests.post('your_webhook_url', json={'title': title, 'message': message})
        pass