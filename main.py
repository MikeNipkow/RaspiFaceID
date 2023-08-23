import datetime
import logging
import os
import time
from threading import Thread

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
    image = face_handler.get_history_image(image_id)
    if image is None:
        return "File not found", 404

    return send_file(image, "image/png")


@app.route("/authorized")
def authorized():
    return face_handler.get_authorized_persons()


@app.route("/authorized-create/<name>", methods=["POST"])
def create_authorized(name: str):
    name = name.replace(" ", "")

    if name is None or len(name) == 0:
        return "Invalid name", 405

    if not camera.is_connected():
        return "Camera is not connected", 404

    image = camera.read()
    if image is None:
        return "Can't read image", 503

    result = face_handler.save_authorized_person(image, name)

    if not result:
        return "Failed to save image", 501
    else:
        face_handler.load_images()
        return authorized()


@app.route("/authorized-delete/<image>", methods=["POST"])
def delete_authorized(image: str):
    result = face_handler.delete_authorized_person(image)

    if not result:
        return "Failed to delete image", 501
    else:
        face_handler.load_images()
        return authorized()


@app.route("/authorized/<image_id>")
def authorized_image(image_id: str):
    image = face_handler.get_authorized_image(image_id)
    if image is None:
        return "File not found", 404

    return send_file(image, "image/png")


def run_api():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    thread = Thread(target=run_api)
    thread.daemon = True
    thread.start()

while True:
    time.sleep(1)
