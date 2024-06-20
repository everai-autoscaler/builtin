from __future__ import annotations

import logging
import re
import typing
import datetime
from zoneinfo import ZoneInfoNotFoundError
from crontab import CronTab
import pytz

logger = logging.getLogger(__name__)


class TimeMatchDecorator:
    tz: datetime.tzinfo
    matchers: typing.List[typing.Tuple[str, CronTab, str]]
    data: typing.Dict[str, str]

    def __init__(self, timezone: typing.Optional[str] = None, **kwargs) -> None:
        """
        assume basic arguments is:
        min_workers: 1
        max_workers: 3
        max_queue_size: 2
        max_idle_time: 120
        scale_up_step: 2

        # match condition and decide prefix, prefixed arguments(only set what is needed) will overwrite basic arguments
        timezone: null  # default is utc
        match(* 9-22 * * 1-5): weekday_day_
        match(* 23,0-8 * * 1-5): weekday_night_
        match(* 9-23,0 * * 6,7): weekend_day_
        match(* 1-8 * * 6,7): weekend_night_
        weekday_day_min_workers: 5
        weekday_day_max_workers: 50

        weekday_night_min_worker: 2
        weekday_night_max_worker: 5

        weekend_day_min_worker: 10
        weekend_day_max_worker: 80
        weekend_day_max_idle_time: 300
        weekend_day_scale_up_step: 5

        weekend_night_min_worker: 2
        weekend_night_max_worker: 5
        """
        try:
            self.tz = pytz.utc if timezone is None else pytz.timezone(timezone)
        except ZoneInfoNotFoundError:
            logging.warning(f'invalid time zone `{timezone}`, use utc')
            self.tz = pytz.utc

        self.matchers = []

        matcher_keys = []
        for k in kwargs.keys():
            result = re.match("^match[(]([0-9,*/-]+(?: [0-9,*/-]+){4})[)]$", k)
            if result is None:
                continue

            keys = list(result.groups())
            if len(keys) == 1:
                cron = CronTab(f'* {keys[0]} *')
                self.matchers.append((keys[0], cron, kwargs[k]))
                matcher_keys.append(k)

        for k in matcher_keys:
            kwargs.pop(k)

        self.data = {k: str(v) for k, v in kwargs.items()}

    def now(self) -> datetime.datetime:
        return datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(self.tz)

    def __call__(self, arguments: typing.Dict[str, str], mock_now: typing.Optional[datetime.datetime] = None) -> typing.Dict[str, str]:
        real_now = self.now()
        now = mock_now if mock_now is not None else real_now

        result = arguments.copy()

        for matcher in self.matchers:
            if matcher[1].test(now):
                logger.debug(f'now: {now.strftime("%Y-%m-%dT%H:%M:%S%z")} matcher: {matcher[0]}, prefix: {matcher[2]}')
                prefix = matcher[2]
                update_dict = {k.removeprefix(prefix): v for k, v in self.data.items() if k.startswith(prefix)}
                logger.debug(f'setting: {self.data}\nupdate_dict: {update_dict}')
                result.update(update_dict)

        return result

    @classmethod
    def name(cls) -> str:
        return 'time-match'

    @classmethod
    def from_arguments(cls, arguments: typing.Dict[str, str]) -> TimeMatchDecorator:
        return TimeMatchDecorator(**arguments)
