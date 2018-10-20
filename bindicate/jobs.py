
import logging
import random
import time
import timeit

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class TimeLimitException(Exception): pass

class TimeLimitedJob(object):
    def __init__(self, app, time_limit):
        self.app = app
        self.time_limit = time_limit

        self.clock_limit = None


    def enter(self):
        self.start_clock = timeit.default_timer()
        if self.time_limit is not None:
            self.clock_limit = self.start_clock + self.time_limit


    def check_timeout(self):
        if self.time_limit is not None:
            clock_now = timeit.default_timer()
            if clock_now < self.start_clock:
                LOGGER.warning("Time stepped backward (possible wrap): %.3f < %3f.  Resetting start time", clock_now, self.start_clock)
                self.start_clock = clock_now
            elif clock_now > self.clock_limit:
                message = "Time limit exceeded - job ran for %.3f seconds" % (clock_now - self.start_clock)
                raise TimeLimitException(message)


class LightTickerJob(TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app
        self.count = 0


    def enter(self):
        TimeLimitedJob.enter(self)
        self.start_clock = timeit.default_timer()
        sleep_time = random.randint(1,20)
        LOGGER.info("Entered LightTickerJob %d, will sleep for %f seconds", self.count, sleep_time)
        for i in range(0, sleep_time):
            time.sleep(1)
            self.check_timeout()
        LOGGER.info("Exited LightTickerJob %d", self.count)
        self.count += 1
