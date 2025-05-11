from datetime import datetime, timezone, timedelta


def split_interval_by_days(start: datetime, end: datetime):
    start_index = start

    while start_index.date() < end.date():
        current_end = datetime.combine(
            start_index.date(), datetime.max.time(), tzinfo=timezone.utc
        )
        yield (start_index, current_end)
        start_index = current_end + timedelta(microseconds=1)

    yield (start_index, end)
