import logging
import time
from threading import Thread

import cv2


class Camera:
    stream_link: str
    capture = None

    connected: bool = False
    last_frame = None

    def __init__(self, stream_link):
        self.stream_link = stream_link

        self.connect()

        self.buffer_thread = Thread(target=self.__reader)
        self.buffer_thread.daemon = True
        self.buffer_thread.start()

        self.connection_thread = Thread(target=self.check_connection)
        self.connection_thread.daemon = True
        self.connection_thread.start()

    # Handle connection.
    def check_connection(self):
        while True:
            if not self.is_connected():
                # Check last known state.
                if self.connected:
                    logging.warning("Lost connecting to video stream...")

                self.disconnect()
                self.connect()

            time.sleep(5)

    # Grab frames as soon as they are available.
    def __reader(self):
        while True:
            if self.is_connected():
                success, frame = self.capture.read()
                if success:
                    self.last_frame = frame
                else:
                    logging.warning("Failed to read image. Disconnecting...")
                    self.disconnect()

                cv2.waitKey(1)

    def is_connected(self):
        return self.capture is not None and self.capture.isOpened()

    # Connect to video device.
    def connect(self):
        logging.info(f"Trying to connect to video stream: {self.stream_link}")
        try:
            self.capture = cv2.VideoCapture(int(self.stream_link) + cv2.CAP_DSHOW)
        except ValueError:
            self.capture = cv2.VideoCapture(self.stream_link)

        # Check if stream is reconnected.
        if self.is_connected():
            logging.info("Successfully connected to the video stream.")
            self.connected = True
        else:
            logging.warning("Failed to connect to the video stream.")
            self.connected = False

    def disconnect(self):
        if self.is_connected():
            self.capture.release()

        self.connected = False

    def read(self):
        if not self.is_connected():
            return None

        return None if self.last_frame is None else self.last_frame.copy()
