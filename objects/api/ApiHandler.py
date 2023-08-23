import logging

from objects.Camera import Camera
from objects.Config import Config
from objects.FaceHandler import FaceHandler
from objects.RaspberryPi import RaspberryPi


class ApiHandler:

    config: Config
    camera: Camera
    pi: RaspberryPi
    face_handler: FaceHandler

    def __init__(self, config: Config, camera: Camera, pi: RaspberryPi, face_handler: FaceHandler):
        self.config = config
        self.camera = camera
        self.pi = pi
        self.face_handler = face_handler

    def get_authorized_persons(self) -> list[str]:
        json = []
        for person in self.face_handler.authorized_persons:
            json.append(person.to_json())

        return json

    def get_history(self):
        json = []
        for file in self.face_handler.get_history_image_files():
            split = file.split("_")

            if len(split) != 3:
                logging.warning(f"Failed to split history image into details: {file}")
                continue

            split_date = split[0].split(".")
            year = split_date[0]
            month = split_date[1]
            day = split_date[2]

            split_time = split[1].split(".")
            hour = split_time[0]
            minute = split_time[1]
            second = split_time[2]

            name = split[2].replace(".png", "")

            json.append({
                "name": name,
                "file": file,
                "timestamp": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second
                }
            })
        return json
