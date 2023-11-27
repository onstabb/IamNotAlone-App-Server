from datetime import datetime, timedelta, timezone


def get_aware_datetime_now(*, delta_days: int = 0) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=delta_days)
