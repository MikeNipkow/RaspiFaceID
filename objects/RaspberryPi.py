import logging
import time
from threading import Thread

import pigpio

from objects.Timer import Timer


class RaspberryPi:
    ip_address: str
    gpio_id: int
    duration: float
    invert_output: bool

    pi: pigpio

    timer: Timer = Timer()

    current_state: bool = False
    toggle_allowed: bool = True

    connected: bool = False

    def __init__(self, ip_address: str, gpio_id: int, duration: float, invert_output: bool):
        self.ip_address = ip_address
        self.gpio_id = gpio_id
        self.duration = duration
        self.invert_output = invert_output

        if self.duration <= 0:
            self.duration = 1

        self.connect()

        self.thread = Thread(target=self.__check_timer)
        self.thread.daemon = True
        self.thread.start()

    def __check_timer(self):
        while True:
            if not self.is_connected():
                if self.connected:
                    logging.warning("Lost connection to RaspberryPi...")
                    self.connected = False

                self.connect()
                time.sleep(60)
                continue

            if self.timer.is_expired() and self.current_state:
                self.switch_gpio(False)

            time.sleep(0.1)

    def is_connected(self):
        return False if self.pi is None else self.pi.connected

    def connect(self):
        # Connect to pi.
        logging.info(f"Trying to establish the connection to RaspberryPi on: {self.ip_address}")
        self.pi = pigpio.pi(self.ip_address)

        # Log if the connection was successful or not.
        if self.pi.connected:
            logging.info("Successfully connected to RaspberryPi.")
        else:
            logging.warning("Failed to connect to RaspberryPi.")

    def set_toggle_allowed(self, allow_toggle):
        self.toggle_allowed = allow_toggle

        if not self.toggle_allowed:
            self.switch_gpio(False)

    def switch_gpio(self, state: bool, seconds: float = 3):
        if not self.is_connected():
            logging.warning("Tried to toggle gpio while pi is not connected.")
            return False

        if seconds <= 0:
            seconds = self.duration

        if state is not self.current_state:
            logging.info("Opening door..." if state else "Closing door...")

        if state:
            self.timer.start(seconds)
        else:
            self.timer.stop()

        self.pi.write(self.gpio_id, state if not self.invert_output else not state)
        self.current_state = state
