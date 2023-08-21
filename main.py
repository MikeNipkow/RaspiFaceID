import logging

from objects.Camera import Camera
from objects.Config import Config
from objects.FaceHandler import FaceHandler
from objects.FaceRecognizer import FaceRecognizer
from objects.RaspberryPi import RaspberryPi

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
