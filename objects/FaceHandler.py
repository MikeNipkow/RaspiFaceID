import glob
import logging
import os.path
from datetime import datetime

import cv2
import face_recognition

from objects.AuthorizedPerson import AuthorizedPerson
from objects.util.faceutils import find_faces
from objects.util.fileutils import list_files


def convert_string_to_path(raw_string):
    return os.path.normpath(raw_string)


def print_capture_info(name):
    logging.info("Person found: " + name)


class FaceHandler:
    image_path: str = os.path.join("data", "images")
    history_path: str = os.path.join("data", "history")

    # List of all authorized persons and their faces.
    authorized_persons = []
    temp_authorized_persons = []
    encoded_faces = []
    temp_encoded_faces = []

    def setup_folders(self):
        os.makedirs(self.history_path)
        os.makedirs(self.image_path)

    def load_images(self):
        self.setup_folders()
        path = self.image_path

        # Loop through every file in the folder.
        for file in list_files(path):
            file_path = os.path.join(path, file)

            if " " in file:
                logging.warning(f"Cannot load image with white-spaces: {file}")
                continue

            image = cv2.imread(file_path)
            if image is None:
                logging.warning(f"Failed to read image file: {file}")
                continue

            # Get faces out of the image.
            face_locations, encoded_faces, amount = find_faces(image)

            # Handle amount of faces in the image.
            if amount == 0:
                # Get name of the person by filename.
                name = file.split(".")[0].split("_")[0]

                # Add person to the whitelist.
                authorized_person = AuthorizedPerson(name, file, image, encoded_faces[0])
                self.temp_authorized_persons.append(authorized_person)
                self.temp_encoded_faces.append(encoded_faces[0])
            else:
                logging.warning(f"{amount} faces found in image {file} - Deleting...")
                os.remove(file_path)
                continue

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

    # Get certain authorized image
    def get_authorized_image(self, name: str):
        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.image_path + "/" + name)))
        return None if len(list_of_files) == 0 else list_of_files[0]

    # Get authorized images
    def get_authorized_images(self):
        # Create folders if they do not exist
        if not os.path.isdir(self.root_path):
            os.mkdir(self.root_path)
        if not os.path.isdir(self.history_path):
            os.mkdir(self.history_path)

        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.image_path + "/*")))
        return list_of_files

    # Get authorized persons.
    def get_authorized_persons(self):
        authorized = []
        images = self.get_authorized_images()

        for file in images:
            assert isinstance(file, str)
            file_name = file.replace(os.path.dirname(file), "").replace("/", "").replace("\\", "")
            file_name_no_ending = file_name.replace(".png", "").replace(".jpg", "")

            split = file_name_no_ending.split("_")

            name = split[0]

            authorized.append({
                "endpoint": f"/authorized/{file_name}",
                "name": name,
                "file": file_name
            })

        return authorized

    def delete_authorized_person(self, image_name: str):
        file = self.image_path + "/" + image_name
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file)
            return True

        return False

    # Save frame.
    def save_authorized_person(self, img, name):
        # Dir path.
        dir_path = self.image_path

        # Create dir.
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass

        current_datetime = datetime.now()
        month = current_datetime.month if current_datetime.month >= 10 else f"0{current_datetime.month}"
        day = current_datetime.day if current_datetime.day >= 10 else f"0{current_datetime.day}"
        hour = current_datetime.hour if current_datetime.hour >= 10 else f"0{current_datetime.hour}"
        minute = current_datetime.minute if current_datetime.minute >= 10 else f"0{current_datetime.minute}"
        second = current_datetime.second if current_datetime.second >= 10 else f"0{current_datetime.second}"
        date = "%s.%s.%s" % (current_datetime.year, month, day)
        time = "%s.%s.%s" % (hour, minute, second)
        filename = convert_string_to_path(dir_path + "/" + name + "_" + date + "_" + time + ".png")
        result = cv2.imwrite(filename, img)

        # Log message.
        logging.info("Successfully added image of authorized person." if result else
                     "Could not save the image of the authorized person.")

        return result

    # Frame face in image
    @staticmethod
    def frame_face(frame, verified, name, left, top, right, bottom):
        color = (0, 255, 0) if verified else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        print_capture_info(name)

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
        month = current_datetime.month if current_datetime.month >= 10 else f"0{current_datetime.month}"
        day = current_datetime.day if current_datetime.day >= 10 else f"0{current_datetime.day}"
        hour = current_datetime.hour if current_datetime.hour >= 10 else f"0{current_datetime.hour}"
        minute = current_datetime.minute if current_datetime.minute >= 10 else f"0{current_datetime.minute}"
        second = current_datetime.second if current_datetime.second >= 10 else f"0{current_datetime.second}"
        date = "%s.%s.%s" % (current_datetime.year, month, day)
        time = "%s.%s.%s" % (hour, minute, second)
        filename = convert_string_to_path(dir_path + "/" + date + "_" + time +
                                          ("_" + person_name if len(person_name) > 0 else "") + ".png")
        result = cv2.imwrite(filename, img)

        # Log message.
        logging.info("Successfully saved image of authorized person." if result else
                     "Could not save the image of the authorized person.")

        self.cleanup_history()

    def get_history_images(self, reverse: bool = True):
        # Create folders if they do not exist
        if not os.path.isdir(self.root_path):
            os.mkdir(self.root_path)
        if not os.path.isdir(self.history_path):
            os.mkdir(self.history_path)

        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.history_path + "/*.png")), reverse=reverse)
        return list_of_files

    def get_history_image(self, name: str):
        list_of_files = sorted(filter(os.path.isfile, glob.glob(self.history_path + "/" + name)), reverse=True)
        return None if len(list_of_files) == 0 else list_of_files[0]

    def get_history(self):
        history = []
        images = self.get_history_images()

        for file in images:
            assert isinstance(file, str)
            file_name = file.replace(os.path.dirname(file), "").replace("/", "").replace("\\", "")

            split = file_name.split("_")

            if len(split) != 3:
                logging.warning(f"Failed to split history image into details: {file_name}")
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

            history.append({
                "endpoint": f"/history/{file_name}",
                "name": name,
                "timestamp": {
                    "year": year,
                    "month": month,
                    "day": day,
                    "hour": hour,
                    "minute": minute,
                    "second": second
                }
            })

        return history

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
