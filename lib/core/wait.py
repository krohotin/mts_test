# -*- coding: utf-8 -*-
import time
from selenium.common.exceptions import TimeoutException

from .config import Config


class Wait:
    def __init__(self, driver, timeout=Config.wait_timeout, poll_frequency=Config.pool_frequency):
        self._driver = driver
        self._timeout = timeout
        self._poll = poll_frequency if poll_frequency != 0 else Config.pool_frequency

    def until(self, method, message=''):
        if self._timeout != 0:
            end_time = time.time() + self._timeout
            while True:
                try:
                    value = method(self._driver)
                    if value:
                        return value
                except:
                    pass
                time.sleep(self._poll)
                if time.time() > end_time:
                    break
            raise TimeoutException("""
                failed while waiting %s seconds with step %s second to assert not %s%s
            """ % (self._timeout, self._poll, method.__class__.__name__, message))

    def bool(self, method):
        if self._timeout != 0:
            try:
                self.until(method)
                return True
            except TimeoutException:
                return False
