
import hashlib
import logging
import requests
import threading
import vobject

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

import job_base

class JobLoadCalendar(job_base.TimeLimitedJob):
    def __init__(self, app, time_limit=None):
        job_base.TimeLimitedJob.__init__(self, app, time_limit)
        self.app = app
        self.count = 0
        self.last_calendar_hash = None
        self.app.calendar = vobject.newFromBehavior('vcalendar')
        self.app.calendar_lock = threading.Lock()



    def load_calendar(self):
        if not self.app.config.has_option('bindicator', 'calendar_url'):
            LOGGER.info('[bindicator]/calendar_url not configured, so not loading calendar')

        calendar_url = self.app.config.get('bindicator', 'calendar_url')

        headers = {
            'Referer': 'https://github.com/sloe/bindicator',
            'User-Agent': 'github.com/sloe/bindicator'
        }

        get_reply = requests.get(calendar_url, headers=headers)

        content_hash = hashlib.sha1(get_reply.content).digest()

        if content_hash == self.last_calendar_hash:
            # Not effective because UUIDs change
            LOGGER.debug("New calendar hash matches last, so not updating")
            return

        LOGGER.debug("Taking calendar lock to load calendar")

        with self.app.calendar_lock:
            self.app.calendar = vobject.readOne(get_reply.content)
            self.last_calendar_hash = content_hash
            self.last_calendar_content = get_reply.content


    def enter(self):
        job_base.TimeLimitedJob.enter(self)
        LOGGER.info("Entered JobLoadCalendar %d", self.count)
        self.load_calendar()
        LOGGER.info("Exited JobLoadCalendar %d", self.count)
        self.count += 1
