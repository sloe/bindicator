
import datetime
import logging
import pytz
import random
import time
import timeit

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

import derive_colours
import job_base

class JobLightTicker(job_base.TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        job_base.TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app
        self.count = 0
        self.derive_colours = derive_colours.DeriveColours(app)


    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        time_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) # + datetime.timedelta(days=1)
        derived_colours = self.derive_colours.derive_colours(time_utc)

        sleep_time = random.randint(1,4)
        LOGGER.info("Entered LightTickerJob %d, will sleep for %f seconds", self.count, sleep_time)
        for i in range(0, sleep_time):
            time.sleep(1)
            self.check_timeout()
        LOGGER.info("Exited LightTickerJob %d", self.count)
        self.count += 1
