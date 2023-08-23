# This class is used to store the data of an authorized person.
class AuthorizedPerson:
    # Data.
    name: str = None
    file_name: str = None
    file_path: str = None
    image = None
    encoded_face = None

    # Constructor.
    def __init__(self, name, file_name, file_path, image, encoded_face):
        self.name = name
        self.file_name = file_name
        self.file_path = file_path
        self.image = image
        self.encoded_face = encoded_face

    def to_json(self):
        return {
            "name": self.name,
            "file": self.file_name
        }
