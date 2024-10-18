import requests
from datetime import date

def get_public_ip():
    """
    Fetches the public IP address of the current machine by making a request 
    to an external service (https://api.ipify.org).

    Returns:
        str: The public IP address if the request is successful.
        str: An error message if the request fails.
    """
    try:
        response = requests.get('https://api.ipify.org?format=json')
        public_ip = response.json()['ip']
        return public_ip
    except Exception as e:
        return f"Error occurred: {e}"

class Database:
    """
    A class that simulates basic database operations for managing video files.
    
    Attributes:
        video_count (int): A class-level counter to track the number of videos created.
        current_date (date): A class-level attribute storing the current date.
    """
    video_count = 1
    current_date = date.today()

    def __init__(self):
        """
        Initializes a new instance of the Database class, setting the directory
        where videos will be saved.
        
        Attributes:
            directory (str): The path to the directory where video files are stored.
        """
        self.directory = "../videos/"
    
    def create_video(self):
        """
        Creates a new video file name using the current date and video count.

        Returns:
            str: The full path of the video file created.
        """
        video = self.directory + str(date.today()) + str(Database.video_count)
        Database.video_count += 1  # Corrected this line to increment the class-level video count
        Database.current_date = date.today()  # Updates the current date to today's date
        return video
