from datetime import datetime, timedelta

from pytz import utc


def get_aware_datetime_now(*, delta_days: int = 0) -> datetime:
    return datetime.now(utc) + timedelta(days=delta_days)
