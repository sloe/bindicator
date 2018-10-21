

import apscheduler.schedulers.blocking
import apscheduler.triggers.combining
import apscheduler.triggers.interval

import logging
import pytz
import threading

from . import job_light_ticker
from . import job_load_calendar

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class Bindicate(object):
    def __init__(self, app):
        self.app = app


    def configure_scheduler(self):
        self.app.scheduler_lock = threading.Lock()
        self.app.scheduler = apscheduler.schedulers.blocking.BlockingScheduler(
            timezone=pytz.utc
        )


    def configure_jobs(self):
        # Calendar loader
        self.load_calendar_job = job_load_calendar.JobLoadCalendar(self.app, time_limit=300)
        # Add immediate job
        trigger = apscheduler.triggers.combining.AndTrigger([apscheduler.triggers.interval.IntervalTrigger(minutes=5)])
        self.app.scheduler.add_job(
            self.load_calendar_job.enter,
            id='load_calendar_job',
            misfire_grace_time=300,
            name='Load calendar',
            replace_existing=True,
            trigger=trigger)


        self.light_ticker_job = job_light_ticker.JobLightTicker(self.app, time_limit=5)
        self.app.scheduler.add_job(
            self.light_ticker_job.enter,
            id='light_ticker_job',
            misfire_grace_time=5,
            name='Minute ticker',
            replace_existing=True,
            trigger='interval',
            seconds=5)


    def setup(self):
        self.configure_scheduler()
        self.configure_jobs()


    def enter(self):
        LOGGER.info("Entered Bindicate app")
        self.app.scheduler.start()



