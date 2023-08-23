import logging
import os.path
from datetime import datetime

import cv2

from objects.AuthorizedPerson import AuthorizedPerson
from objects.util.faceutils import find_faces
from objects.util.fileutils import list_files, delete_file
from objects.util.timeutils import datetime_to_string


class FaceHandler:
    image_path: str = os.path.join("data", "images")
    history_path: str = os.path.join("data", "history")
    max_history_images = 100

    # List of all authorized persons and their faces.
    authorized_persons: list[AuthorizedPerson] = []
    encoded_faces = []

    def setup_folders(self):
        os.makedirs(self.history_path)
        os.makedirs(self.image_path)

    def load_images(self):
        self.setup_folders()
        path = self.image_path

        # Clear current authorized faces
        self.authorized_persons.clear()
        self.encoded_faces.clear()

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
                authorized_person = AuthorizedPerson(name, file, file_path, image, encoded_faces[0])
                self.authorized_persons.append(authorized_person)
                self.encoded_faces.append(encoded_faces[0])
            else:
                logging.warning(f"{amount} faces found in image {file} - Deleting...")
                os.remove(file_path)
                continue

        # Print authorized persons.
        # Check how many persons are authorized.
        amount = len(self.authorized_persons)
        logging.info(f"Found {amount} authorized persons" + (":" if amount > 0 else "."))

        # Loop through every person to print information about them.
        for authorized_person in self.authorized_persons:
            logging.info(" - " + authorized_person.name + ": " + authorized_person.file_path)

    def get_authorized_person_image_file(self, file: str):
        return os.path.join(self.image_path, file)

    def get_history_image_file(self, file: str):
        return os.path.join(self.history_path, file)

    # Get authorized image files
    def get_authorized_image_files(self):
        return list_files(self.image_path)

    # Get authorized image files
    def get_history_image_files(self):
        return list_files(self.history_path)

    def delete_authorized_person(self, image_name: str, reload: bool = True) -> bool:
        self.setup_folders()

        file = self.get_authorized_person_image_file(image_name)
        result = delete_file(file)

        if reload:
            self.load_images()

        return result

    # Save frame.
    def create_authorized_person(self, image, name: str, reload: bool = True) -> bool:
        self.setup_folders()

        dt_string = datetime_to_string(datetime.now())
        file_name = f"{name}_{dt_string}.png"
        file = os.path.join(self.image_path, file_name)

        result = cv2.imwrite(file, image)

        # Log message.
        logging.info("Successfully added image of authorized person." if result else
                     "Could not save the image of the authorized person.")

        if reload:
            self.load_images()

        return result

    def delete_history_image(self, file_name: str) -> bool:
        self.setup_folders()

        file = self.get_history_image_file(file_name)
        return delete_file(file)

    # Save frame.
    def save_frame_in_history(self, image, person_name: str):
        self.setup_folders()

        dt_string = datetime_to_string(datetime.now())
        file_name = f"{dt_string}_{person_name}.png"
        file = os.path.join(self.history_path, file_name)

        result = cv2.imwrite(file, image)

        # Log message.
        logging.info("Successfully saved image of authorized person." if result else
                     "Could not save the image of the authorized person.")

        self.cleanup_history()

    # Handle a maximum amount of images stored on the disk.
    def cleanup_history(self):
        self.setup_folders()

        image_files = self.get_history_image_files()
        amount = len(image_files)
        if amount <= self.max_history_images:
            return

        to_delete = amount - self.max_history_images
        deleted = 0

        for file_name in image_files:
            if deleted >= to_delete:
                break

            self.delete_history_image(file_name)
            logging.info("Deleted old history image: " + file_name)
            deleted += 1
