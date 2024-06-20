import zoneinfo
from datetime import datetime
import unittest

import pytz

from everai_autoscaler.builtin.decorator.arguments.time_match import TimeMatchDecorator


class TestTimeMatch(unittest.TestCase):
    def test_time_match(self):
        mock_now = datetime(2024, 6, 19, 11, 55, 2)

        arguments = {
            "timezone": "Asia/Shanghai",
            "match(* 11 * * 1-5)": "weekday_day_",
            "weekday_day_max_workers": "3",
        }

        orig_arg = {
            "min_workers": '4',
            "max_workers": '40',
        }

        dec = TimeMatchDecorator.from_arguments(arguments)
        output = dec(orig_arg, mock_now=mock_now)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '3')
