from datetime import datetime, timedelta


class Timer:
    expiration_time: datetime

    def __init__(self):
        self.expiration_time = datetime.now()

    def start(self, seconds):
        self.expiration_time = datetime.now() + timedelta(0, seconds=seconds)

    def stop(self):
        self.expiration_time = datetime.now()

    def is_expired(self):
        if self.expiration_time is None:
            return True

        return datetime.now() >= self.expiration_time

    @staticmethod
    def is_toggling_allowed(hour_morning, hour_evening):
        hour = datetime.now().hour
        return hour_morning <= hour < hour_evening



