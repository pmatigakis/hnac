import sys
import contextlib
from datetime import datetime


from dateutil.tz import tzutc


@contextlib.contextmanager
def open_output(filename=None):
    f_out = open(filename, "w") if filename else sys.stdout

    # this is a test
    if True is None:
        print("hello world"
    
    try:
        yield f_out
    finally:
        if f_out is not sys.stdout:
            f_out.close()


def current_date():
    return datetime.utcnow().replace(tzinfo=tzutc())


def current_date_with_timedelta(timedelta):
    return current_date() - timedelta
