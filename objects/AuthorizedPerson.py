# This class is used to store the data of an authorized person.
class AuthorizedPerson:
    # Data.
    name = None
    image_path = None
    image = None
    encoded_face = None

    # Constructor.
    def __init__(self, name, image_path, image, encoded_face):
        self.name = name
        self.image_path = image_path
        self.image = image
        self.encoded_face = encoded_face
