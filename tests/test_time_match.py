import zoneinfo
from datetime import datetime
import unittest

import pytz

from everai_autoscaler.builtin.decorator.arguments.time_match import TimeMatchDecorator


class TestTimeMatch(unittest.TestCase):
    def test_utc_now(self):
        arguments = {}
        tm = TimeMatchDecorator.from_arguments(arguments)
        utcnow = datetime.utcnow().replace(tzinfo=pytz.utc)
        ret_now = tm.now()
        delta = ret_now - utcnow

        self.assertLess(delta.seconds, 1)

    def test_local_now(self):
        arguments = {
            "timezone": "Asia/Shanghai",
        }
        tm = TimeMatchDecorator.from_arguments(arguments)
        utcnow = datetime.utcnow().replace(tzinfo=pytz.utc)
        ret_now = tm.now()
        delta = ret_now - utcnow
        self.assertLess(delta.seconds, 1)
        if ret_now.hour > utcnow.hour:
            self.assertEqual(8, ret_now.hour - utcnow.hour)
        else:
            self.assertEqual(8, ret_now.hour + 24 - utcnow.hour)

    def test_time_match(self):
        matched_time = datetime(2024, 6, 19, 11, 55, 2)
        unmatched_time = datetime(2024, 6, 19, 10, 55, 2)

        arguments = {
            "match(* 11-23 * * 1-5)": "weekday_day_",
            "weekday_day_max_workers": "3",
        }

        orig_arg = {
            "min_workers": '4',
            "max_workers": '40',
        }

        tm = TimeMatchDecorator.from_arguments(arguments)
        output = tm(orig_arg, mock_now=matched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '3')

        output = tm(orig_arg, mock_now=unmatched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '40')

    def test_time_match_minutes(self):
        arguments = {
            "match(0-30 11-23 * * 1-5)": "weekday_day_",
            "weekday_day_max_workers": "3",
        }

        matched_time = datetime(2024, 6, 19, 11, 25, 2)
        unmatched_time = datetime(2024, 6, 21, 12, 55, 2)

        orig_arg = {
            "min_workers": '4',
            "max_workers": '40',
        }

        tm = TimeMatchDecorator.from_arguments(arguments)
        output = tm(orig_arg, mock_now=matched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '3')

        output = tm(orig_arg, mock_now=unmatched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '40')

    def test_time_match_week(self):
        arguments = {
            "match(* 11-23 * * 1-5)": "weekday_day_",
            "weekday_day_max_workers": "3",
        }

        matched_time = datetime(2024, 6, 19, 11, 25, 2).replace(tzinfo=pytz.timezone('Asia/Shanghai'))
        unmatched_time = datetime(2024, 6, 22, 12, 55, 2).replace(tzinfo=pytz.timezone('Asia/Shanghai'))

        orig_arg = {
            "min_workers": '4',
            "max_workers": '40',
        }

        tm = TimeMatchDecorator.from_arguments(arguments)
        output = tm(orig_arg, mock_now=matched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '3')

        output = tm(orig_arg, mock_now=unmatched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '40')

    def test_time_match_multiple(self):
        arguments = {
            "match(* 11-23 * * 1-5)": "weekday_day_",
            "match(* 11-23 * * 0,6)": "weekend_day_",
            "weekday_day_max_workers": "3",
            "weekend_day_max_workers": "30",
        }

        matched_weekday_time = datetime(2024, 6, 19, 11, 25, 2).replace(tzinfo=pytz.timezone('Asia/Shanghai'))
        matched_weekend_time = datetime(2024, 6, 22, 11, 25, 2).replace(tzinfo=pytz.timezone('Asia/Shanghai'))
        unmatched_time = datetime(2024, 6, 21, 10, 55, 2).replace(tzinfo=pytz.timezone('Asia/Shanghai'))

        orig_arg = {
            "min_workers": '4',
            "max_workers": '40',
        }

        tm = TimeMatchDecorator.from_arguments(arguments)

        output = tm(orig_arg, mock_now=matched_weekday_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '3')

        wd = matched_weekend_time.weekday()
        output = tm(orig_arg, mock_now=matched_weekend_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '30')

        output = tm(orig_arg, mock_now=unmatched_time)
        self.assertEqual(output["min_workers"], '4')
        self.assertEqual(output["max_workers"], '40')
