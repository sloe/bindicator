#!/usr/bin/env python

import argparse
import logging

import bindicate.bindicate

class App(object):
    def __init__(self):
        pass


    def parse_args(self):
        parser = argparse.ArgumentParser(description='Bin indication daemon.')

        self.options = parser.parse_args()


    def configure_logging(self):
        logging.basicConfig(level=logging.DEBUG)



    def enter(self):
        app = bindicate.bindicate.Bindicate(self)
        app.setup()
        app.enter()


if __name__ == '__main__':
    app = App()
    app.parse_args()
    app.configure_logging()
    app.enter()

