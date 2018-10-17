from unittest import TestCase, main
from datetime import datetime

from dateutil.tz import tzutc, tzoffset

from hnac.cli.datatypes import date_string


class DateStringTests(TestCase):
    def test_parse_date_string(self):
        date = date_string("2018/01/01 00:00:00")

        self.assertEqual(
            date,
            datetime(2018, 1, 1, tzinfo=tzutc())
        )

    def test_parse_date_string_with_timezone(self):
        date = date_string("2018/01/01 00:00:00 +03:00")

        self.assertEqual(
            date,
            datetime(2017, 12, 31, 21, 0, 0, tzinfo=tzutc())
        )

    def test_adjust_datetime_to_utc(self):
        date = datetime(
            2018, 1, 1, 12, 0, 0,
            tzinfo=tzoffset(None, 2 * 60 * 60)
        )

        adjusted_date = date_string(date)

        self.assertEqual(
            adjusted_date,
            datetime(2018, 1, 1, 10, 0, 0, tzinfo=tzutc())
        )

    def test_do_not_adjust_utc_datetime(self):
        date = datetime(2018, 1, 1, 12, 0, 0, tzinfo=tzutc())
        adjusted_date = date_string(date)

        self.assertEqual(
            adjusted_date,
            datetime(2018, 1, 1, 12, 0, 0, tzinfo=tzutc())
        )


if __name__ == "_main__":
    main()
