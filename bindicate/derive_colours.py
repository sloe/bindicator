
import datetime
import itertools
import hashlib
import logging


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class DeriveColours(object):

    def __init__(self, app):
        self.app = app


    def derive_bin_colours(self, time_utc):

        sec_before_binday = int(self.app.config.get('bindicator', 'sec_before_binday'))
        sec_after_binday = int(self.app.config.get('bindicator', 'sec_after_binday'))

        current_events = []
        with self.app.calendar_lock:
            for calendar_event in self.app.calendar:
                # If start time is within the bracketed range
                if (time_utc > calendar_event['start_time'] - datetime.timedelta(seconds=sec_before_binday)and
                    time_utc < calendar_event['start_time'] + datetime.timedelta(seconds=sec_after_binday)):
                    current_events.append(calendar_event['name'])

        LOGGER.info("Current events: %s", current_events)


    def derive_colours(self, time_utc):
        bin_colours = self.derive_bin_colours(time_utc)
        colours = []
        colours.append(bin_colours)

        return colours
