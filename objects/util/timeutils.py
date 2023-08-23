from datetime import datetime


def datetime_to_string(dt: datetime):
    month = dt.month if dt.month >= 10 else f"0{dt.month}"
    day = dt.day if dt.day >= 10 else f"0{dt.day}"
    hour = dt.hour if dt.hour >= 10 else f"0{dt.hour}"
    minute = dt.minute if dt.minute >= 10 else f"0{dt.minute}"
    second = dt.second if dt.second >= 10 else f"0{dt.second}"

    date = "%s.%s.%s" % (dt.year, month, day)
    time = "%s.%s.%s" % (hour, minute, second)

    return f"{date}_{time}"
