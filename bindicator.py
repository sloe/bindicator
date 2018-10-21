#!/usr/bin/env python

import argparse
import ConfigParser
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

