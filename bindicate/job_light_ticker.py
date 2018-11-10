
import copy
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

        self.lights = []
        for tp_bulb_ip in self.app.options.tp_bulb_ips:
            self.lights.append(light_tp.LightTP(tp_bulb_ip, 9999, socket_timeout=2))


    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        self.count += 1
        LOGGER.info("Entered LightTickerJob %d", self.count)
        time_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) # + datetime.timedelta(days=1)
        derived_colours = self.colour_deriver.derive_colours(time_utc)

        if derived_colours:
            colour_index = self.count % len(derived_colours)
            current_colour = copy.copy(derived_colours[colour_index])
            current_colour['transition_period'] = int(self.app.options.transition_msec)

            for light in self.lights:
                light.set_colour(current_colour)

        LOGGER.info("Exited LightTickerJob %d", self.count)
