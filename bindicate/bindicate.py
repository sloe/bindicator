

import apscheduler.schedulers.blocking

import logging
import pytz

from . import jobs

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class Bindicate(object):
    def __init__(self, app):
        self.app = app


    def configure_scheduler(self):
        self.scheduler = apscheduler.schedulers.blocking.BlockingScheduler(
            timezone=pytz.utc
        )


    def configure_jobs(self):
        self.light_ticker_job = jobs.LightTickerJob(self.app, time_limit=5)
        self.scheduler.add_job(
            self.light_ticker_job.enter,
            args=[],
            id='light_ticker_job',
            misfire_grace_time=5,
            name='Minute ticker',
            trigger='interval',
            seconds=5)


    def setup(self):
        self.configure_scheduler()
        self.configure_jobs()


    def enter(self):
        LOGGER.info("Entered Bindicate app")
        self.scheduler.start()



