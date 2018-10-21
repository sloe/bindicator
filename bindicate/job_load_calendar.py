
import logging
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
        self.count = 0
        self.app.calendar = vobject.newFromBehavior('vcalendar')
        self.app.calendar_lock = threading.Lock()

    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        LOGGER.info("Entered JobLoadCalendar %d", self.count)
        LOGGER.debug("Taking calendar lock")
        with self.app.calendar_lock:
            pass

        with self.app.scheduler_lock:
            self.app.scheduler.reschedule_job('load_calendar_job', trigger='interval', minutes=5)

        LOGGER.info("Exited JobLoadCalendar %d", self.count)
        self.count += 1
