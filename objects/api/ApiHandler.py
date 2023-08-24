import logging

from flask import send_file

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

    def get_status(self):
        return {
            "camera": {
                "connected": self.camera.is_connected(),
                "stream_url": self.camera.stream_link
            },
            "pi": {
                "connected": self.pi.is_connected(),
                "ip_address": self.pi.ip_address,
                "gpio_id": self.pi.gpio_id,
                "gpio_state": self.pi.current_state
            }
        }, 200

    def get_image(self, image):
        if image is None:
            return "File not found.", 404

        return send_file(image, "image/png")

    def get_authorized_person_image(self, image_id: str):
        image = self.face_handler.get_authorized_person_image_file(image_id)
        return self.get_image(image)

    def get_history_image(self, image_id: str):
        image = self.face_handler.get_history_image_file(image_id)
        return self.get_image(image)

    def get_authorized_persons(self) -> list[str]:
        json = []
        for person in self.face_handler.authorized_persons:
            json.append(person.to_json())

        return json

    def create_authorized_person(self, name: str):
        if name is None or len(name) == 0 or " " in name:
            return "Invalid name.", 400

        image = self.camera.read()
        if image is None or not self.camera.is_connected():
            return "Camera error.", 503

        result = self.face_handler.create_authorized_person(image, name)
        if result:
            return self.get_authorized_persons()
        else:
            return "Failed to save the image.", 500

    def delete_authorized_person(self, file_name):
        result = self.face_handler.delete_authorized_person(file_name)

        if result:
            return self.get_authorized_persons()
        else:
            return "Failed to delete image.", 500

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

    def delete_history(self, file_name):
        result = self.face_handler.delete_history_image(file_name)

        if result:
            return self.get_history()
        else:
            return "Failed to delete image.", 500
