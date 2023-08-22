import logging
import os

import cv2
from flask import Flask, make_response, send_file

from objects.Camera import Camera
from objects.Config import Config
from objects.FaceHandler import FaceHandler
from objects.FaceRecognizer import FaceRecognizer
from objects.RaspberryPi import RaspberryPi
from flask_cors import CORS

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

config = Config("config.ini")

camera = Camera(config.camera_stream_link())

pi = RaspberryPi(config.pi_ip_address(), config.pi_gpio_id(), config.pi_output_duration(), config.pi_invert_output())

face_handler = FaceHandler()
face_handler.load_images()

face_recognizer = FaceRecognizer(config, camera, pi, face_handler)

# API
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    print("Received")
    return {
        "camera": {
            "connected": camera.is_connected()
        },
        "pi": {
            "connected": pi.is_connected(),
            "gpio_state": pi.current_state
        }
    }


@app.route("/history")
def history():
    return face_handler.get_history()


@app.route("/history/<image_id>")
def history_image(image_id: str):
    if not image_id.isdigit():
        return make_response(404)

    images = face_handler.get_history_images()
    if int(image_id) < 0 or int(image_id) >= len(images):
        return make_response(404)

    return send_file(os.path.normpath(images[int(image_id)]), "image/png")


app.run(debug=False)

while True:
    pass
