import logging
import time
from threading import Thread

import cv2
import face_recognition

from objects import Config, Camera, RaspberryPi, FaceHandler
from objects.Timer import Timer
from objects.util.faceutils import find_faces, frame_face


class FaceRecognizer:
    last_frame = None

    def __init__(self, config: Config, camera: Camera, pi: RaspberryPi, face_handler: FaceHandler):
        self.config = config
        self.camera = camera
        self.pi = pi
        self.face_handler = face_handler

        self.thread = Thread(target=self.__check_image)
        self.thread.daemon = True
        self.thread.start()

    def __check_image(self):
        while True:
            frame_bgr = self.camera.read()
            if frame_bgr is None:
                continue
            if self.last_frame is not None and (self.last_frame == frame_bgr).all():
                continue

            self.last_frame = frame_bgr

            # Convert BGR to RGB.
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            # Null check
            if frame_rgb is None:
                continue

            # Get all faces in current frame.
            face_locations, face_encodings, amount = find_faces(frame_rgb)

            # Var to check if door will be opened by this frame.
            door_opened_before = self.pi.current_state

            # Check if any face is authorized.
            any_authorized_face = False

            # Get name of authorized person
            person_name = ""

            # Copy data to prevent thread problems
            encoded_faces = self.face_handler.encoded_faces.copy()
            authorized_persons = self.face_handler.authorized_persons.copy()

            # Loop through all the faces found in the current frame.
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Var to check if the person is authorized or not
                authorized = False

                # Compare face with the authorized faces.
                matches = face_recognition.compare_faces(encoded_faces, face_encoding,
                                                         tolerance=self.config.face_recognition_tolerance())

                # Check if a face matches.
                for i in range(len(matches)):
                    # Continue, if it doesn't match 100%.
                    if not matches[i]:
                        continue

                    # Get name.
                    name = authorized_persons[i].name
                    if len(person_name) <= 0:
                        person_name = name

                    # Draw a frame around the face.
                    frame_face(frame_bgr, True, name, left, top, right, bottom)
                    logging.info(f"Found authorized person: {name}")

                    # End loop
                    authorized = True
                    any_authorized_face = True

                # Also frame face, if the person is unknown.
                if not authorized:
                    name = self.config.settings_unknown_name()
                    frame_face(frame_bgr, False, name, left, top, right, bottom)
                    logging.info(f"Person found: {name}")

            # Check if toggling is allowed
            if Timer.is_toggling_allowed(self.config.settings_allow_toggle_from(),
                                         self.config.settings_allow_toggle_to()):
                # Open or close door
                if any_authorized_face:
                    self.pi.switch_gpio(True, self.pi.duration)

                # Save the image, if the door will be opened by this image.
                if not door_opened_before and self.pi.current_state:
                    self.face_handler.save_frame(frame_bgr, person_name)

        self.camera.disconnect()
        self.pi.switch_gpio(False)


