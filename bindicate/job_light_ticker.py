
import logging
import random
import time
import timeit

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

import job_base

class JobLightTicker(job_base.TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        job_base.TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app
        self.count = 0


    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        self.start_clock = timeit.default_timer()
        sleep_time = random.randint(1,4)
        LOGGER.info("Entered LightTickerJob %d, will sleep for %f seconds", self.count, sleep_time)
        for i in range(0, sleep_time):
            time.sleep(1)
            self.check_timeout()
        LOGGER.info("Exited LightTickerJob %d", self.count)
        self.count += 1
