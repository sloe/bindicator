
import datetime
import hashlib
import logging
import pytz
import requests
import threading
import vobject

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

import job_base

class JobLoadCalendar(job_base.TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        job_base.TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app

        self.calendar_change_count = 0
        self.count = 0
        self.vobject_calendar = vobject.newFromBehavior('vcalendar')

        self.app.calendar = None
        self.app.calendar_lock = threading.Lock()


    def load_calendar(self):
        if not self.app.config.has_option('bindicator', 'calendar_url'):
            LOGGER.info('[bindicator]/calendar_url not configured, so not loading calendar')

        calendar_url = self.app.config.get('bindicator', 'calendar_url')

        headers = {
            'Referer': 'https://github.com/sloe/bindicator',
            'User-Agent': 'github.com/sloe/bindicator'
        }

        get_reply = requests.get(calendar_url, headers=headers)

        self.vobject_calendar = vobject.readOne(get_reply.content)
        self.last_calendar_content = get_reply.content


    @staticmethod
    def datetime_to_utc(dt):
        if isinstance(dt, datetime.date):
            return datetime.datetime.combine(dt, datetime.datetime.min.time().replace(tzinfo=pytz.utc))
        elif dt.tzinfo is None:
            return dt.replace(tzinfo=pytz.utc)
        else:
            return dt.astimezone(pytz.utc)


    def parse_calendar(self):
        calendar_events = []
        for vevent in self.vobject_calendar.vevent_list:
            dtstart = getattr(vevent, 'dtstart', None)
            dtend = getattr(vevent, 'dtend', None)
            summary = getattr(vevent, 'summary', None)

            if dtstart and hasattr(dtstart, 'value'):
                start_time = self.datetime_to_utc(dtstart.value)

                if dtend and hasattr(dtend, 'value'):
                    end_time = self.datetime_to_utc(dtend.value)
                else:
                    # Assume all day event
                    end_time = start_time + datetime.timedelta(hours=24)

                if summary and hasattr(summary, 'value'):
                    name = summary.value
                else:
                    name = '<Unknown>'

                time_record = dict(
                    end_time=end_time,
                    name=name,
                    start_time=start_time
                )
                calendar_events.append(time_record)

        def _compare(a, b):
            time_cmp = cmp(a['start_time'], b['start_time'])
            if time_cmp == 0:
                return cmp(a['name'], b['name'])
            else:
                return time_cmp

        sorted_calendar = sorted(calendar_events, _compare)

        rewrite_calendar = False

        if len(sorted_calendar) < 5:
            LOGGER.error("Ignoring unreasonable calendar size %d", len(sorted_calendar))
        elif not self.app.calendar:
            rewrite_calendar = True
        elif self.app.calendar == sorted_calendar:
            LOGGER.debug("Calendar unchanged")
            self.calendar_change_count = 0
        else:
            LOGGER.info("Waiting for consistent reads of new calendar (%d)", self.calendar_change_count)
            if sorted_calendar == self.last_sorted_calendar:
                self.calendar_change_count += 1
                if self.calendar_change_count >= 5:
                    self.app.bindicate.add_event("INFO_CALENDAR_CHANGE", "Accepted changed calendar", self.last_calendar_content)
                    rewrite_calendar = True
            else:
                self.calendar_change_count = 0

        if rewrite_calendar:
            LOGGER.info("Accepting calendar with %d events from %s to %s",
                        len(sorted_calendar),
                        sorted_calendar[0]['start_time'],
                        sorted_calendar[-1]['start_time'])

            with self.app.calendar_lock:
                self.app.calendar = sorted_calendar


            self.calendar_change_count = 0

        self.last_sorted_calendar = sorted_calendar


    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        LOGGER.info("Entered JobLoadCalendar %d", self.count)
        self.load_calendar()
        self.parse_calendar()
        LOGGER.info("Exited JobLoadCalendar %d", self.count)
        self.count += 1
