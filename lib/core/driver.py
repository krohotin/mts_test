# -*- coding: utf-8 -*-
import time

from selenium.webdriver.remote.webdriver import WebDriver

from .config import Config
from .element import Element
from .service import correct_url
from .wait import Wait

# глобальный текущий драйвер
current = None


def replace_current_driver(selenium_driver):
    """Заменяет текущий глобальный драйвер на указанный"""
    global current
    current = ExtendedSeleniumDriver(selenium_driver)
    return current


class ExtendedSeleniumDriver:
    """
    Класс представляет собой расширение класса WebDriver из оригинального  selenium-а.
    """
    def __init__(self, selenium_driver):
        self.driver = selenium_driver

    def __getattr__(self, item):
        return getattr(self.driver, item)

    def unwrap(self):
        """ Метод возвращает объект оригинального WebDriver-а """
        if isinstance(self.driver, WebDriver):
            return self.driver

    @property
    def _xpath_prefix(self):
        return '//*'

    @property
    def browser_name(self):
        """ Имя браузера """
        return str(self.driver.name)

    @property
    def window_handles(self):
        return self.driver.window_handles

    @property
    def browser_version(self):
        """ Версия браузера """
        return str(self.driver.capabilities['version'])

    @property
    def operating_system(self):
        """ Рабочая ОС """
        return str(self.driver.capabilities['platform'])

    def add_base_url(self, url=None):
        if url is None or not isinstance(url, str):
            pass
        else:
            Config.base_url = url
        return self

    ####################################################################################################################

    def size(self, size):
        """ Устанавливает размер окна браузера. Размер задается строкой вида "ШИРИНАхДЛИНА" в пикселях, а также словами
            full (во весь экран) и fullscreen (полноэкранный режим, нажатие клавищи F11) """
        if size == 'full':
            self.driver.maximize_window()
        elif size == "default":
            pass
        elif size == "fullscreen":
            self.driver.maximize_window()
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element_by_css_selector('html').send_keys(Keys.F11)
        else:
            try:
                w, h = size.split("x")
                self.driver.set_window_size(w, h)
            except:
                pass
        return self

    def get(self, url=""):
        """ Перейти по url. В случае отсутствия в начале строки http:// или https:// по умолчанию сам подставаляет
            https:// """
        url = correct_url(url)
        self.driver.get(url)
        return self

    def raw_get(self, url):
        """ Переход без подстановок """
        self.driver.get(url)
        return self

    @property
    def url(self):
        """ Возвращает текущий url страницы """
        return str(self.driver.current_url)

    @property
    def html(self):
        """ Возвращает весь код страницы """
        return str(self.driver.page_source)

    @property
    def title(self):
        """ Возвращает заголовок страницы """
        return str(self.driver.title)

    def execute_script(self, script, *args):
        """ Выполняет на странице произвольный js-скрипт """
        return self.driver.execute_script(script, *args)

    @property
    def time_load(self):
        """ Возвращает время загрузки страницы """
        time_load_end = self.driver.execute_script("return window.performance.timing.loadEventEnd;")
        time_navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart;")
        return float((time_load_end - time_navigation_start) / 1000)

    def pause(self, s=1):
        """ Пауза выполнения """
        time.sleep(s)
        return self

    def sleep(self, s=1):
        """ Пауза выполнения """
        time.sleep(s)
        return self

    def close(self):
        """ Закрыть страницу """
        self.driver.close()
        return self

    def quit(self):
        """ Закончить сессию работы с браузером """
        self.driver.quit()

    def close_and_quit(self):
        """ Объединение предыдущих методов в один """
        self.driver.close()
        self.driver.quit()

    def back(self):
        """ Шаг назад в истории браузера """
        self.driver.back()
        return self

    def forward(self):
        """ Шаг врепед в истории браузера """
        self.driver.forward()
        return self

    def refresh(self):
        """ Обновить страницу """
        self.driver.refresh()
        return self

    def delete_cookies(self):
        """ Удалить все куки """
        self.driver.delete_all_cookies()
        return self

    def screenshot(self, filename):
        """ Сделать скриншот текущей страницы """
        self.driver.get_screenshot_as_file(filename)
        return self

    @property
    def page_size(self):
        """ Определяет размер всей старницы, включая той части что скрыта скролом """
        height = """var scrollHeight = Math.max(
              document.body.scrollHeight, document.documentElement.scrollHeight,
              document.body.offsetHeight, document.documentElement.offsetHeight,
              document.body.clientHeight, document.documentElement.clientHeight
            );
            return scrollHeight; """
        width = """var scrollWidth = Math.max(
              document.body.scrollWidth, document.documentElement.scrollWidth,
              document.body.offsetWidth, document.documentElement.offsetWidth,
              document.body.clientWidth, document.documentElement.clientWidth
            );
            return scrollWidth; """
        w = self.driver.execute_script(height)
        h = self.driver.execute_script(width)
        return [int(h), int(w)]

    @property
    def work_size(self):
        """ Определяет размер рабочей области браузера """
        w = self.driver.execute_script("return document.body.clientWidth")
        h = self.driver.execute_script("return window.innerHeight")
        return [int(h), int(w)]

    @property
    def window_size(self):
        """ Определяет размер окна браузера (рабочая область + поля + панель меню) """
        rz = self.driver.get_window_size()
        w = rz["width"]  # Ширина
        h = rz["height"]  # Высота
        return [int(w), int(h)]

    @property
    def monitor_size(self):
        """ Определяет разрешение монитора (с помощью js) """
        w = self.driver.execute_script("var a = window.screen.width; return a")
        h = self.driver.execute_script("var a = window.screen.height; return a")
        return [int(w), int(h)]

    ####################################################################################################################

    def scroll_down(self, step=50):
        """ Одиночный скрол вниз на опеределнное кол-во пикселей (шаг) """
        self.driver.execute_script("scrollTo(0, window.pageYOffset+%s)" % step)
        return self

    def scroll_up(self, step=50):
        """ Одиночный вниз вверх на опеределнное кол-во пикселей (шаг) """
        self.driver.execute_script("scrollTo(0, window.pageYOffset-%s)" % step)
        return self

    def scroll_down_loop(self, n, step=50, tsleep=0.1):
        """ Циклический скрол вниз на опеределнное кол-во шагов """
        for i in range(1, n):
            self.driver.execute_script("scrollTo(0, window.pageYOffset+%s)" % step)
            time.sleep(tsleep)
        return self

    def scroll_up_loop(self, n, step=50, tsleep=0.1):
        """ Циклический скрол вверх на опеределнное кол-во шагов """
        for i in range(1, n):
            self.driver.execute_script("scrollTo(0, window.pageYOffset-%s)" % step)
            time.sleep(tsleep)
        return self

    def scroll_down_full(self, step=50, tsleep=0.1):
        """ Пошаговый скрол страницы до самого низа страницы (прокрутка) """
        h = self.driver.get_window_size()["height"]
        h_full = self.driver.execute_script("var a = document.documentElement.scrollHeight; return a;")
        n = int((h_full - h) / step) + 1
        for i in range(1, n + 1):
            self.driver.execute_script("scrollTo(0, window.pageYOffset+%s)" % step)
            time.sleep(tsleep)
        return self

    def scroll_up_full(self, step=50, tsleep=0.1):
        """ Пошаговый скрол страницы до самого верха страницы (прокрутка) """
        h = self.driver.get_window_size()["height"]
        h_full = self.driver.execute_script("var a = document.documentElement.scrollHeight; return a;")
        n = int((h_full - h) / step) + 1
        for i in range(1, n + 1):
            self.driver.execute_script("scrollTo(0, window.pageYOffset-%s)" % step)
            time.sleep(tsleep)
        return self

    def scroll_to(self, y):
        """ Прокрутка по оси Y относительно всей страницы до указанной координаты (абсолютные координаты) """
        self.driver.execute_script("window.scrollTo({:d}, {:d})".format(0, y))
        return self

    def scroll_by(self, y):
        """ Прокрутка по оси Y относительно текущиего места на указанное кол-во пикселей """
        self.driver.execute_script("window.scrollBy({:d}, {:d})".format(0, y))
        return self

    def scroll_top(self):
        """ Прокрутка к самому верху страницы """
        self.driver.execute_script("window.scrollTo({:d}, {:d})".format(0, 0))
        return self

    def scroll_bottom(self):
        """ Прокрутка к самому низу страницы """
        h_full = self.driver.execute_script("var a = document.documentElement.scrollHeight; return a;")
        self.driver.execute_script("window.scrollTo({:d}, {:d})".format(0, h_full))
        return self

    ####################################################################################################################

    def wait(self, condition, message="", wait=Config.wait_timeout, pool=Config.pool_frequency):
        """ Ожидание """
        Wait(self, wait, pool).until(condition, message)
        return self

    ####################################################################################################################

    def focused(self):
        """ Возвращает элемент в фокусе """
        return Element("", element=self.driver.switch_to.active_element)

    def is_any_page_loaded(self):
        """ Возвращает True если загружена какая-либо станица """
        return bool("http" in self.driver.current_url)
