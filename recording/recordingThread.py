import threading
import time
from datetime import date

from database.db import Database
from network.network import send_email

class RecordingThread(threading.Thread):
    def __init__(self, alert, create_video):
        super().__init__()
        self.alert = alert
        self.create_video = create_video
        self.alert.set()
        self.create_video.set()
        self.database = Database()

    def run(self):
        if not self.alert.is_set():
            video = self.database.create_video()
            #todo: Add a way to route this back...
            message_details = {
                "subject" : "Suspicious Activity",
                "body" : "Susicious activity around car at time " + str(date.today())
            }
            send_email(message_details)
            self.alert.set()
    
    


            

if __name__ == "__main__":
    alert = threading.Event()  # This acts like an atomic boolean
    recording_thread = RecordingThread(alert)

    # Start the recording thread
    recording_thread.start()

    # Simulate running for some time before alert
    time.sleep(5)

    # Wait for the thread to finish
    recording_thread.join()
    print("Recording thread has stopped.")
