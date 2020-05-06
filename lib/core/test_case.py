# -*- coding: utf-8 -*-
from unittest import TestCase

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import wait as selenium_wait
from lib.core.finder import s
from lib.core.config import Config

from .config import Config
from .tools import get, Browser


class SeleniumTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = Browser(Config.browser_name)

    # noinspection PyUnresolvedReferences
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def wait(self, method, **kwargs):
        """Шорткат для selenium'овского wait с учетом наших настроек"""
        kwargs.setdefault('poll_frequency', Config.pool_frequency)
        kwargs.setdefault('timeout', Config.wait_timeout)
        wait = selenium_wait.WebDriverWait(self, **kwargs)
        return wait.until(method)

    def wait_assert(self, method, **kwargs):
        """wait для ассертов: в конце будет не таймаут, а эксепшн зафейлившегося ассерта"""
        def _f(_):
            try:
                method(self)
                return True
            except AssertionError:
                return False

        try:
            self.wait(_f, **kwargs)
        except TimeoutException:
            method(self)

    def assertTitle(self, title):
        """ Проверка заголовка страницы, с ожиданием """
        self.wait_assert(lambda _: self.assertEqual(self.driver.title, title))

    def assertTitleContains(self, title):
        """ Проверка заголовка страницы (части), с ожиданием """
        self.wait_assert(lambda _: self.assertTrue(title in self.driver.title))

    def assertUrlContains(self, url):
        """ Проверка url страницы, с ожиданием """
        self.assertTrue(url in self.driver.current_url)

    def assertElementVisible(self, elem):
        """ Проверка видимости элемента/элементов на странице, с ожиданием """
        self.wait_assert(lambda _: self.assertTrue(elem.is_visible()))

    def assertElementInteraction(self, elem):
        """ Проверка доступности элемента/элементов для взаимодействия (видимость, enable), с ожиданием """
        self.wait_assert(lambda _: self.assertTrue(elem.is_interaction()))

    def assertTextVisible(self, *args):
        """ Проверка нахождения на странице текста и того что он видим """
        for text in args:
            self.wait_assert(lambda _: self.assertTrue(s(text=text).is_visible()))

    def assertTextNotVisible(self, *args):
        """ Проверка ненахождения на странице текста (отсутствует элемент или текст невидим) """
        for text in args:
                self.wait_assert(lambda _: self.assertTrue(s(text=text, wait=0).is_not_visible()))

    def assertElementNotFound(self, elem):
        """ Проверка ненахождения элемента/элементов на странице, с ожиданием """
        self.wait_assert(lambda _: self.assertTrue(elem.not_exist()))
