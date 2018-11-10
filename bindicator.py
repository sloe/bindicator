#!/usr/bin/env python

import argparse
import ConfigParser
import dateutil.parser
import json
import logging
import os

import bindicate.bindicate

class App(object):
    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.delayed_log_functions = []
        self.logger = None

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Bin indication daemon.')
        parser.add_argument('--config', nargs='?', help='Path to config file')

        self.options = parser.parse_args()


    def configure_logging(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('bindicator.App')
        self.logger.setLevel(logging.DEBUG)

        for delayed_log_function in self.delayed_log_functions:
            delayed_log_function()


    def load_config(self):
        config_files = []
        if self.options.config:
            config_files += self.options.config
        else:
            script_path = os.path.dirname(os.path.abspath(__file__))
            static_config = os.path.join(script_path, 'config.txt')
            sample_config = os.path.join(script_path, 'config.txt.sample')

            if os.path.isfile(static_config):
                config_files.append(static_config)
            elif os.path.isfile(sample_config):
                self.delayed_log_functions.append(lambda: self.logger.warning("Loading sample config file"))
                config_files.append(sample_config)

        for config_file in config_files:
            self.delayed_log_functions.append(lambda: self.logger.info('Reading config file %s', config_file))
            self.config.read(config_file)

        float_elems = (
             ('bindicator', 'light_change_sec'),
             ('bindicator', 'nightlight_hysteresis'),
             ('bindicator', 'sec_before_binday'),
             ('bindicator', 'sec_after_binday'),
             ('bindicator', 'transition_msec')
         )

        for section, option in float_elems:
            if self.config.has_option(section, option):
                try:
                    config_value = self.config.get(section, option)
                    if config_value:
                        float_value = float(config_value)
                        setattr(self.options, option, float_value)
                except Exception as exc:
                    raise Exception("Failed to parse '%s' as floating point: %s" % (config_value, exc))

        json_elems = (
            ('bindicator', 'signal_black_bin'),
            ('bindicator', 'signal_blue_bin'),
            ('bindicator', 'signal_green_bin'),
            ('bindicator', 'signal_nightlight'),
            ('bindicator', 'tp_bulb_ips'),
        )

        for section, option in json_elems:
            if self.config.has_option(section, option):
                try:
                    config_value = self.config.get(section, option)
                    if config_value:
                        json_value = json.loads(config_value)
                        setattr(self.options, option, json_value)
                except Exception as exc:
                    raise Exception("Failed to parse '%s' as JSON: %s" % (config_value, exc))


        time_elems = (
             ('bindicator', 'utc_dark_summer'),
             ('bindicator', 'utc_dark_winter'),
             ('bindicator', 'utc_light_summer'),
             ('bindicator', 'utc_light_winter')
         )

        for section, option in time_elems:
            if self.config.has_option(section, option):
                try:
                    config_value = self.config.get(section, option)
                    if config_value:
                        time_value = dateutil.parser.parse(config_value).time()
                        setattr(self.options, option, time_value)
                except Exception as exc:
                    raise Exception("Failed to parse '%s' as time: %s" % (config_value, exc))


    def enter(self):
        self.bindicate = bindicate.bindicate.Bindicate(self)
        self.bindicate.setup()
        self.bindicate.enter()


if __name__ == '__main__':
    app = App()
    app.parse_args()
    app.load_config()
    app.configure_logging()
    app.enter()

