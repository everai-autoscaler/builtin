from datetime import datetime
import unittest
import pytz


class TestTimezone(unittest.TestCase):
    def test_timezone(self):
        z = pytz.timezone("Asia/Shanghai")

        now = datetime.now()
        local_now = z.localize(now)
        l1_timestamp = int(local_now.timestamp())

        utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_from_utc = utc_time.astimezone(z)

        l2_timestamp = int(local_from_utc.timestamp())

        self.assertEqual(l1_timestamp, l2_timestamp)
        # z2 = ZoneInfo("s/b")
        # print(z2)
