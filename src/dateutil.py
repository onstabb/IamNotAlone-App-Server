from datetime import datetime, date

from pytz import utc


def get_aware_datetime_now() -> datetime:
    return datetime.now(utc)


def get_age(birthday: date) -> int:
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
