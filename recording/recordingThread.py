import threading
import time
from datetime import date

from database.db import Database
from network.network import send_email

class RecordingThread(threading.Thread):
    """
    A thread class responsible for simulating the process of recording a video 
    and sending an email alert if suspicious activity is detected.

    Attributes:
        alert (threading.Event): An event used to signal when to stop or start recording.
        create_video (threading.Event): An event used to trigger the creation of a video file.
        database (Database): An instance of the Database class for managing video records.
    """
    
    def __init__(self, alert, create_video):
        """
        Initializes the RecordingThread with provided alert and create_video events.

        Args:
            alert (threading.Event): Used to manage the alert state of the recording.
            create_video (threading.Event): Used to trigger the creation of video files.
        """
        super().__init__()
        self.alert = alert
        self.create_video = create_video
        self.alert.set()  # Set the alert to an active state initially
        self.create_video.set()  # Set the video creation to active state initially
        self.database = Database()  # Initialize a database instance for video records

    def run(self):
        """
        The main function of the thread. When the alert is not set, it creates a video file 
        and sends an email alert with details about the suspicious activity.
        """
        if not self.alert.is_set():
            video = self.database.create_video()  # Create a video file
            # TODO: Add a way to route this back to the alert system or log it
            message_details = {
                "subject": "Suspicious Activity",
                "body": "Suspicious activity around car at time " + str(date.today())
            }
            send_email(message_details)  # Send an email alert
            self.alert.set()  # Set the alert to active state after handling the event

if __name__ == "__main__":
    alert = threading.Event()  # This acts like an atomic boolean
    create_video = threading.Event()  # An event to trigger video creation

    # Start the recording thread
    recording_thread = RecordingThread(alert, create_video)
    recording_thread.start()

    # Simulate running for some time before setting the alert
    time.sleep(5)

    # Wait for the recording thread to finish
    recording_thread.join()
    print("Recording thread has stopped.")
