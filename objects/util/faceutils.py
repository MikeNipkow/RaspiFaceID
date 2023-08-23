import cv2
import face_recognition


def find_faces(image):
    face_locations = face_recognition.face_locations(image)
    encoded_faces = face_recognition.face_encodings(image, face_locations)
    amount = len(encoded_faces)

    return face_locations, encoded_faces, amount


# Frame face in image
def frame_face(frame, verified, name, left, top, right, bottom):
    color = (0, 255, 0) if verified else (0, 0, 255)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
