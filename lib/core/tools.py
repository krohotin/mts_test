# -*- coding: utf-8 -*-
# Базовый модуль с набором функций
from selenium import webdriver

from ..core import driver
from .config import Config
from ..core.driver import ExtendedSeleniumDriver


def Browser(browser_name, *args, remote_address='', language='ru', **kwargs):
    """
    Создать объект браузера по указанному имени и сохранить его в буфере.
    ! Язык можно указать только у локального хрома
    """
    if remote_address:
        if browser_name == 'firefox':
            sel_driver = webdriver.Remote(remote_address, webdriver.DesiredCapabilities.FIREFOX)
        elif browser_name == 'chrome':
            sel_driver = webdriver.Remote(remote_address, webdriver.DesiredCapabilities.CHROME)
        elif browser_name == 'opera':
            sel_driver = webdriver.Remote(remote_address, webdriver.DesiredCapabilities.OPERA)
        else:
            raise ValueError(browser_name)
    else:
        if browser_name == 'firefox':
            sel_driver = webdriver.Firefox(*args, **kwargs)
        elif browser_name == 'chrome':
            options = webdriver.ChromeOptions()

            # применяем желаемый язык
            if language:
                options.add_experimental_option('prefs', {'intl.accept_languages': language + ',en-us,en'})

            sel_driver = webdriver.Chrome(*args, chrome_options=options, **kwargs)
        elif browser_name == 'opera':
            sel_driver = webdriver.Opera(*args, **kwargs)
        elif browser_name == 'ie':
            sel_driver = webdriver.Ie(capabilities={'ignoreZoomSetting': True}, *args, **kwargs)
        else:
            raise ValueError(browser_name)

    our_driver = driver.replace_current_driver(sel_driver)
    our_driver.size(Config.base_size)
    return our_driver


def get(url=Config.base_url):
    """ Вызов метода get """
    if isinstance(driver.current, ExtendedSeleniumDriver):
        return driver.current.get(url)


def refresh():
    driver.current.refresh()


def title():
    return driver.current.title


def close():
    driver.current.close()
    driver.current.quit()
