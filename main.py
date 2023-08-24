import datetime
import logging
import os
import time
from threading import Thread

import cv2
import flask
from flask import Flask, make_response, send_file

from objects.Camera import Camera
from objects.Config import Config
from objects.FaceHandler import FaceHandler
from objects.FaceRecognizer import FaceRecognizer
from objects.RaspberryPi import RaspberryPi
from flask_cors import CORS

from objects.api.ApiHandler import ApiHandler

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
api_handler = ApiHandler(config, camera, pi, face_handler)
app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return api_handler.get_status()


@app.route("/history")
def history():
    return api_handler.get_history()


@app.route("/history/<arg>", methods=["GET", "DELETE"])
def history_image(arg: str):
    if flask.request.method == "DELETE":
        return api_handler.delete_history(arg)
    else:
        return api_handler.get_history_image(arg)


@app.route("/authorized")
def authorized():
    return api_handler.get_authorized_persons()


@app.route("/authorized/<arg>", methods=["GET", "POST", "DELETE"])
def authorized_image(arg: str):
    if flask.request.method == "POST":
        return api_handler.create_authorized_person(arg)
    elif flask.request.method == "DELETE":
        return api_handler.delete_authorized_person(arg)
    else:
        return api_handler.get_authorized_person_image(arg)


def run_api():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    thread = Thread(target=run_api)
    thread.daemon = True
    thread.start()

while True:
    time.sleep(1)
