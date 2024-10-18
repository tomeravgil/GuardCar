import requests
from datetime import date

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        public_ip = response.json()['ip']
        return public_ip
    except Exception as e:
        return f"Error occurred: {e}"

class Database:
    video_count = 1
    current_date = date.today()

    def __init__(self):
        self.directory = "../videos/"
    
    def create_video(self):
        video = self.directory + str(date.today()) + str(Database.video_count)
        video_count +=1
        Database.current_date = date.today()
        return video

