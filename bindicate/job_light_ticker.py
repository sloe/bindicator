
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
import light_tp


class JobLightTicker(job_base.TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        job_base.TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app
        self.count = 0
        self.light_states = {}
        self.colour_deriver = derive_colours.DeriveColours(app)

        self.light = light_tp.LightTP('10.67.64.17', 9999, socket_timeout=2)



    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        time_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) # + datetime.timedelta(days=1)
        derived_colours = self.colour_deriver.derive_colours(time_utc)

        sleep_time = random.randint(1,4)
        LOGGER.info("Entered LightTickerJob %d, will sleep for %f seconds", self.count, sleep_time)

        if self.count % 2 == 0:
            self.light.set_colour(dict(
                brightness=100,
                hue=240,
                on_off=1,
                saturation=95,
                transition_period=2400
            ))
        else:
            self.light.set_colour(dict(
                brightness=50,
                hue=120,
                on_off=1,
                saturation=100,
                transition_period=2400
            ))

        LOGGER.info("Exited LightTickerJob %d", self.count)
        self.count += 1
