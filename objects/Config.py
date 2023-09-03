import logging
import os.path
from configparser import ConfigParser


class Config:
    config_path: str = None
    config: ConfigParser = ConfigParser()

    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        if not os.path.isfile(self.config_path):
            logging.warning(f"Failed to load config file: {self.config_path}")
            return False

        self.config.read(self.config_path)

    def camera_stream_link(self):
        return self.config.get("Camera", "Stream-URL")

    def pi_ip_address(self):
        return self.config.get("Raspberry Pi", "IP-Address")

    def pi_gpio_id(self):
        return self.config.getint("Raspberry Pi", "GPIO")

    def pi_output_duration(self):
        return self.config.getfloat("Raspberry Pi", "OutputDuration")

    def pi_invert_output(self):
        return self.config.getboolean("Raspberry Pi", "InvertOutput")

    def face_recognition_tolerance(self):
        return self.config.getfloat("Face Recognition", "Tolerance")

    def settings_unknown_name(self):
        return self.config.get("Settings", "UnknownName")

    def settings_allow_toggle_from(self):
        return self.config.getint("Settings", "AllowToggleFrom")

    def set_settings_allow_toggle_from(self, toggle_from: int):
        if 0 > toggle_from > 24:
            return False
        self.config.set("Settings", "AllowToggleFrom", str(toggle_from))
        return True

    def settings_allow_toggle_to(self):
        return self.config.getint("Settings", "AllowToggleTo")

    def set_settings_allow_toggle_to(self, toggle_to: int):
        if 0 > toggle_to > 24:
            return False
        self.config.set("Settings", "AllowToggleTo", str(toggle_to))
        return True


