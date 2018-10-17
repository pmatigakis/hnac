from datetime import datetime

from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc


def date_string(value):
    if isinstance(value, datetime):
        return value.astimezone(tzutc())

    dt = parse_date(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzutc())
    else:
        dt = dt.astimezone(tz=tzutc())

    return dt
