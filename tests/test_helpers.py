from unittest import TestCase, main
from unittest.mock import patch
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from hnac.helpers import current_date_with_timedelta


class CurrentDateWithTimedeltaTests(TestCase):
    @patch("hnac.helpers.current_date")
    def test_current_date_with_timedelta(self, current_date_mock):
        current_date_mock.return_value = datetime(2018, 5, 11, tzinfo=tzutc())

        date = current_date_with_timedelta(timedelta(days=1))

        self.assertIsInstance(date, datetime)
        self.assertEqual(
            date,
            datetime(2018, 5, 10, tzinfo=tzutc())
        )


if __name__ == "__main__":
    main()
