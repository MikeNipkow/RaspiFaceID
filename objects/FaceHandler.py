import glob
import logging
import os.path
from datetime import datetime

import cv2
import face_recognition

from objects.AuthorizedPerson import AuthorizedPerson


def convert_string_to_path(raw_string):
    return os.path.normpath(raw_string)


class FaceHandler:
    root_path: str = "data"
    image_path: str = "data/images"
    history_path: str = "data/history"

    # List of all authorized persons and their faces.
    authorized_persons = []
    temp_authorized_persons = []
    encoded_faces = []
    temp_encoded_faces = []

    def load_images(self):
        # Create folders if they do not exist
        if not os.path.isdir(self.root_path):
            os.mkdir(self.root_path)
        if not os.path.isdir(self.image_path):
            os.mkdir(self.image_path)
        if not os.path.isdir(self.history_path):
            os.mkdir(self.history_path)

        # Loop through every file in the folder.
        for file_name in os.listdir(self.image_path):
            image = cv2.imread(self.image_path + "/" + file_name)
            if image is None:
                continue

            # Get name of the person by filename.
            split_file_name = file_name.split("_")
            name = split_file_name[0] if len(split_file_name) > 1 \
                else file_name.replace(".png", "").replace(".jpg", "")

            # Get faces out of the image.
            face_locations = face_recognition.face_locations(image)
            encoded_faces = face_recognition.face_encodings(image, face_locations)

            # Handle amount of faces in the image.
            if len(encoded_faces) <= 0:
                logging.warning(f"No face found in image {file_name} -  Skipping...")
                continue

            elif len(encoded_faces) > 1:
                logging.warning(f"More than one face found in {file_name} - Skipping...")
                continue

            else:
                # Add person to the whitelist.
                authorized_person = AuthorizedPerson(name, file_name, image, encoded_faces[0])
                self.temp_authorized_persons.append(authorized_person)
                self.temp_encoded_faces.append(encoded_faces[0])

        # Move temp vars to live vars.
        self.authorized_persons = self.temp_authorized_persons.copy()
        self.encoded_faces = self.temp_encoded_faces.copy()

        # Clear temporary vars.
        self.temp_authorized_persons.clear()
        self.temp_encoded_faces.clear()

        # Print authorized persons.
        # Check how many persons are authorized.
        amount = len(self.authorized_persons)
        logging.info(f"Found {amount} authorized persons" + (":" if amount > 0 else "."))

        # Loop through every person to print information about them.
        for authorized_person in self.authorized_persons:
            logging.info(" - " + authorized_person.name + ": " + authorized_person.image_path)

    # Frame face in image
    def frame_face(self, frame, verified, name, left, top, right, bottom):
        color = (0, 255, 0) if verified else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        self.print_capture_info(name)

    # Info if person was detected
    def print_capture_info(self, name):
        logging.info("Person found: " + name)

    # Save frame.
    def save_frame(self, img, person_name: str = ""):
        # Dir path.
        dir_path = self.history_path

        # Create dir.
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass

        current_datetime = datetime.now()
        date = "%s.%s.%s" % (current_datetime.year, current_datetime.month, current_datetime.day)
        time = "%s.%s.%s" % (current_datetime.hour, current_datetime.minute, current_datetime.second)
        filename = convert_string_to_path(dir_path + "/" + date + "_" + time +
                                          ("_" + person_name if len(person_name) > 0 else "") + ".png")
        result = cv2.imwrite(filename, img)

        # Log message.
        logging.info("Successfully saved image of authorized person." if result else
                     "Could not save the image of the authorized person.")

        self.cleanup_history()

    def cleanup_history(self):
        max_images = 100

        # Create folders if they do not exist
        if not os.path.isdir(self.root_path):
            os.mkdir(self.root_path)
        if not os.path.isdir(self.history_path):
            os.mkdir(self.history_path)

        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.history_path + "/*")))

        if len(list_of_files) <= max_images:
            return

        to_delete = len(list_of_files) - max_images
        deleted = 0

        for file_name in os.listdir(self.history_path):
            if deleted >= to_delete:
                break

            os.remove(self.history_path + "/" + file_name)
            logging.info("Deleted old history image: " + file_name)
            deleted += 1

    # Get all face locations and encodings in a frame.
    @staticmethod
    def get_face_locations_and_encodings(frame):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        return face_locations, face_encodings
