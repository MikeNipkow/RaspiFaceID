import logging
import time

import cv2
import face_recognition

from objects.Camera import Camera
from objects.Config import Config
from objects.FaceHandler import FaceHandler
from objects.RaspberryPi import RaspberryPi
from objects.Timer import Timer

logging.getLogger().setLevel(logging.INFO)

config = Config("config.ini")

camera = Camera(config.camera_stream_link())

pi = RaspberryPi(config.pi_ip_address(), config.pi_gpio_id(), config.pi_output_duration(), config.pi_invert_output())

face_handler = FaceHandler()
face_handler.load_images()

while True:

    # Check if toggling is allowed
    if not Timer.is_toggling_allowed(config.settings_allow_toggle_from(), config.settings_allow_toogle_to()):
        time.sleep(300)
        continue

    frame_bgr = camera.read()
    if frame_bgr is None:
        continue

    # Convert BGR to RGB.
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # Null check
    if frame_rgb is None:
        continue

    # Get all faces in current frame.
    face_locations, face_encodings = face_handler.get_face_locations_and_encodings(frame_rgb)

    # Var to check if door will be opened by this frame.
    door_opened_before = pi.current_state

    # Check if any face is authorized.
    any_authorized_face = False

    # Get name of authorized person
    person_name = ""

    # Loop through all the faces found in the current frame.
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Var to check if the person is authorized or not
        authorized = False

        # Compare face with the authorized faces.
        matches = face_recognition.compare_faces(face_handler.encoded_faces, face_encoding,
                                                 tolerance=config.face_recognition_tolerance())

        # Check if a face matches.
        for i in range(len(matches)):
            # Continue, if it doesn't match 100%.
            if not matches[i]:
                continue

            # Get name.
            name = face_handler.authorized_persons[i].name
            if len(person_name) <= 0:
                person_name = name

            # Draw a frame around the face.
            face_handler.frame_face(frame_bgr, True, name, left, top, right, bottom)

            # End loop
            authorized = True
            any_authorized_face = True

        # Also frame face, if the person is unknown.
        if not authorized:
            face_handler.frame_face(frame_bgr, False, config.settings_unknown_name(), left, top, right, bottom)

    # Open or close door
    if any_authorized_face:
        pi.switch_gpio(True, pi.duration)

    # Save the image, if the door will be opened by this image.
    if not door_opened_before and pi.current_state:
        face_handler.save_frame(frame_bgr, person_name)

camera.disconnect()
pi.switch_gpio(False)
