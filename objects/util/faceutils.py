import face_recognition


def find_faces(image):
    face_locations = face_recognition.face_locations(image)
    encoded_faces = face_recognition.face_encodings(image, face_locations)
    amount = len(encoded_faces)

    return face_locations, encoded_faces, amount