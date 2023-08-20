import logging
import time
from threading import Thread

import cv2


class Camera:
    stream_link: str
    capture = None

    connected: bool = False

    def __init__(self, stream_link):
        self.stream_link = stream_link

        self.connect()

        self.thread = Thread(target=self.__reader)
        self.thread.daemon = True
        self.thread.start()

    # Grab frames as soon as they are available.
    def __reader(self):
        while True:
            if not self.is_connected():
                if self.connected:
                    logging.warning("Lost connecting to video stream...")

                self.disconnect()
                self.connect()
                time.sleep(5)

            if self.capture is not None:
                ret = self.capture.grab()

    def is_connected(self):
        return self.capture is not None and self.capture.isOpened()

    # Connect to video device.
    def connect(self):
        logging.info(f"Trying to connect to video stream: {self.stream_link}")
        try:
            self.capture = cv2.VideoCapture(int(self.stream_link))
        except ValueError:
            self.capture = cv2.VideoCapture(self.stream_link)

        # Check if stream is reconnected.
        if self.is_connected():
            logging.info("Successfully connected to the video stream.")
            self.connected = True
        else:
            logging.warning("Failed to connect to the video stream.")

    def disconnect(self):
        if self.is_connected():
            self.capture.release()

        self.connected = False

    def read(self):
        if not self.is_connected():
            return None

        success, frame = self.capture.retrieve()
        return frame if success else None
