
import copy
import datetime
import dateutil.parser
import itertools
import hashlib
import logging
import math
import pytz
import re


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class DeriveColours(object):

    def __init__(self, app):
        self.app = app


    def derive_bin_colours(self, time_utc):

        current_events = []
        with self.app.calendar_lock:
            for calendar_event in self.app.calendar or []:
                # If start time is within the bracketed range
                if (time_utc > calendar_event['start_time'] - datetime.timedelta(seconds=self.app.options.sec_before_binday) and
                    time_utc < calendar_event['start_time'] + datetime.timedelta(seconds=self.app.options.sec_after_binday)):
                    current_events.append(calendar_event['name'])


        bin_colours = []

        for current_event in current_events:
            if re.search('black', current_event, re.IGNORECASE):
                bin_colours += self.app.options.signal_black_bin.get('tp', [])
            if re.search('blue', current_event, re.IGNORECASE):
                bin_colours += self.app.options.signal_blue_bin.get('tp', [])
            if re.search('green', current_event, re.IGNORECASE):
                bin_colours += self.app.options.signal_green_bin.get('tp', [])

        LOGGER.info("Current events: %s, colours %s", current_events, bin_colours)
        return bin_colours


    def derive_nightlight_colours(self, time_utc):
        summer_solstice_yday = datetime.datetime(2018, 06, 21).timetuple().tm_yday
        winter_solstice_yday = datetime.datetime(2018, 12, 21).timetuple().tm_yday
        day_of_year = time_utc.timetuple().tm_yday
        summer_fraction = math.cos(math.pi * ((day_of_year - summer_solstice_yday) / 365.0)) ** 2
        winter_fraction = math.cos(math.pi * ((day_of_year - winter_solstice_yday) / 365.0)) ** 2

        def _time_to_seconds(_time, must_be_after=None):
            as_seconds = 3600 * _time.hour + 60 * _time.minute + _time.second
            if must_be_after and as_seconds < must_be_after:
                return 24 * 3600 + as_seconds
            else:
                return as_seconds

        dark_winter_sec = _time_to_seconds(self.app.options.utc_dark_winter)
        dark_summer_sec = _time_to_seconds(self.app.options.utc_dark_summer, dark_winter_sec)
        dark_sec = summer_fraction * dark_summer_sec + winter_fraction * dark_winter_sec

        light_winter_sec = _time_to_seconds(self.app.options.utc_light_winter)
        light_summer_sec = _time_to_seconds(self.app.options.utc_light_summer, light_winter_sec)
        light_sec = summer_fraction * light_summer_sec + winter_fraction * light_winter_sec

        now_sec = _time_to_seconds(time_utc)

        def _min_distance_modulo(_a, _b, _modulo):
            _options = (
                math.fmod(_a - _b, _modulo),
                math.fmod(_a - _b - _modulo, _modulo),
                math.fmod(_a - _b + _modulo, _modulo)
            )

            _sorted_options = sorted(_options, cmp=lambda a, b: cmp(math.fabs(a), math.fabs(b)))

            return (_sorted_options[0])


        min_dark_distance = _min_distance_modulo(now_sec, dark_sec, 24*3600)
        min_light_distance = _min_distance_modulo(now_sec, light_sec, 24*3600)

        if math.fabs(min_dark_distance) < math.fabs(min_light_distance):
            # Closer to dark point so calculate from that
            brightness = 1.1 * (0.5 + math.atan(min_dark_distance / self.app.options.nightlight_hysteresis) / math.pi) - 0.1
        else:
            brightness = 1.1 * (0.5 - math.atan(min_light_distance / self.app.options.nightlight_hysteresis) / math.pi) - 0.1

        nightlight_colours = []

        if brightness > 0:
            colours = self.app.options.signal_nightlight
            for colour in colours.get('tp', []):
                nightlight_colour = copy.copy(colour)
                nightlight_colour['brightness'] = int(min(100, 1 + nightlight_colour.get('brightness', 100) * brightness))
                nightlight_colours.append(nightlight_colour)

        LOGGER.info("Brightness=%.1f", brightness)
        return nightlight_colours


    def derive_colours(self, time_utc):
        # time_utc = dateutil.parser.parse('2018-11-22 01:00:00').replace(tzinfo=pytz.utc)
        bin_colours = self.derive_bin_colours(time_utc)
        colours = []
        colours += bin_colours

        if not colours:
            nightlight_colours = self.derive_nightlight_colours(time_utc)
            colours += nightlight_colours

        if not colours:
            colours += self.app.options.signal_none.get('tp', [])

        return colours
