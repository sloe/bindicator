

import apscheduler.schedulers.blocking
import apscheduler.triggers.combining
import apscheduler.triggers.interval

import datetime
import logging
import pytz
import threading

from . import job_light_ticker
from . import job_load_calendar

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ImmediateIntervalTrigger(apscheduler.triggers.interval.IntervalTrigger):
    def __init__(self, *args, **kwargs):
        apscheduler.triggers.interval.IntervalTrigger.__init__(self, *args, **kwargs)
        self.immediate_trigger_done = False


    def get_next_fire_time(self, previous_fire_time, now):
        if not self.immediate_trigger_done:
            self.immediate_trigger_done = True
            return self.timezone.normalize(now)
        else:
            return apscheduler.triggers.interval.IntervalTrigger.get_next_fire_time(self, previous_fire_time, now)


class Bindicate(object):
    def __init__(self, app):
        self.app = app
        self.events = []


    def add_event(self, code, message, body):
        LOGGER.info("Added event %s: %s (%d)", code, message, len(body))
        self.events.append((code, message, body))


    def configure_scheduler(self):
        self.app.scheduler_lock = threading.Lock()
        self.app.scheduler = apscheduler.schedulers.blocking.BlockingScheduler(
            timezone=pytz.utc
        )


    def configure_jobs(self):
        # Calendar loader
        self.load_calendar_job = job_load_calendar.JobLoadCalendar(self.app, time_limit=300)
        trigger = ImmediateIntervalTrigger(seconds=3600)

        load_calendar_job_obj = self.app.scheduler.add_job(
            self.load_calendar_job.enter,
            id='load_calendar_job',
            misfire_grace_time=30,
            name='Load calendar',
            replace_existing=True,
            trigger=trigger)

        # Light controller
        self.light_ticker_job = job_light_ticker.JobLightTicker(self.app, time_limit=5)
        self.app.scheduler.add_job(
            self.light_ticker_job.enter,
            id='light_ticker_job',
            misfire_grace_time=5,
            name='Minute ticker',
            replace_existing=True,
            trigger='interval',
            seconds=500)


    def setup(self):
        self.configure_scheduler()
        self.configure_jobs()


    def enter(self):
        LOGGER.info("Entered Bindicate app")
        self.app.scheduler.start()



