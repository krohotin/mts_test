# -*- coding: utf-8 -*-
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


class BaseCondition:
    """ Базовое ожидание """

    def __call__(self, driver):
        self.driver = driver
        try:
            return self.apply()
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def __str__(self):
        try:
            return """
            \tfor %s:%s%s
        """ % (self.identity(),
               """
            \t\texpected: """ + str(self.expected()) if (self.expected() is not None) else "",
               """
            \t\t  actual: """ + str(self.actual()) if (self.actual() is not None) else ""
               )
        except Exception as e:
            return "\n type: %s \n msg: %s \n" % (type(e), e)

    def identity(self):
        return "element"

    def expected(self):
        return None

    def actual(self):
        return None

    def apply(self):
        return None


########################################################################################################################


class Title(BaseCondition):
    """ Ожидание нужного заголовка страницы """

    def __init__(self, _title):
        self._title = _title

    def apply(self):
        return self._title == self.driver.title

    def identity(self):
        return "page " + self.driver.url

    def expected(self):
        return '\"' + self._title + '\"'

    def actual(self):
        return '\"' + self.driver.title + '\"'


def ttl(txt):
    return Title(txt)


########################################################################################################################


class URL(BaseCondition):
    """ Ожидание нужного заголовка страницы """

    def __init__(self, _url):
        self._url = _url

    def apply(self):
        return self._url == self.driver.url

    def identity(self):
        return "page " + self.driver.url

    def expected(self):
        return '\"' + self._url + '\"'

    def actual(self):
        return '\"' + self.driver.url + '\"'


def Url(txt):
    return URL(txt)


########################################################################################################################


class URLContains(BaseCondition):
    """ Ожидание нужного заголовка страницы """

    def __init__(self, _url):
        self._url = _url

    def apply(self):
        return self._url in self.driver.url

    def identity(self):
        return "page " + self.driver.url

    def expected(self):
        return '\"' + self._url + '\"'

    def actual(self):
        return '\"' + self.driver.url + '\"'


def url_contains(txt):
    return URLContains(txt)


########################################################################################################################


class TitleContains(BaseCondition):
    """ Ожидание нужного заголовка страницы """

    def __init__(self, _title):
        self._title = _title

    def apply(self):
        return self._title in self.driver.title

    def expected(self):
        return '\"' + self._title + '\"'

    def actual(self):
        return '\"' + self.driver.title + '\"'


def title_contains(txt):
    return TitleContains(txt)


########################################################################################################################


class Text(BaseCondition):
    """ Ожидание нужного текста """

    def __init__(self, _text):
        self._text = _text

    def apply(self):
        return self._text == self.driver.text

    def expected(self):
        return '\"' + self._text + '\"'

    def actual(self):
        return '\"' + self.driver.text + '\"'


def text(txt):
    return Text(txt)


########################################################################################################################


class Text_contains(BaseCondition):
    """ Ожидание вхождения текста """

    def __init__(self, txt):
        self.text_contains = txt

    def apply(self):
        return self.text_contains in self.driver.text

    def expected(self):
        return '\"' + self.text_contains + '\"'

    def actual(self):
        return '\"' + self.driver.text + '\"'


def text_contains(txt):
    return Text_contains(txt)


########################################################################################################################


class Visible(BaseCondition):
    """ Ожидание видимости """

    def apply(self):
        return self.driver.is_visible()

    def expected(self):
        return 'visible'

    def actual(self):
        return 'invisible'


visible = Visible()


########################################################################################################################


class Invisible(BaseCondition):
    """ Ожидание невидимости """

    def apply(self):
        return not self.driver.is_visible()

    def expected(self):
        return 'invisible'

    def actual(self):
        return 'visible'


invisible = Invisible()


########################################################################################################################


class Enable(BaseCondition):
    """ Ожидание возможности взаимодействия """

    def apply(self):
        return self.driver.is_enabled()

    def expected(self):
        return 'enable'

    def actual(self):
        return 'disable'


enable = Enable()


########################################################################################################################


class Disable(BaseCondition):
    """ Ожидание невозможности взаимодействия """

    def apply(self):
        return not self.driver.is_enabled()

    def expected(self):
        return 'disable'

    def actual(self):
        return 'enable'


disable = Disable()


########################################################################################################################


class Interaction(BaseCondition):
    """ Расширенное ожидание возможности взаимодействия """

    def apply(self):
        return self.driver.is_interaction()

    def expected(self):
        return 'interaction'

    def actual(self):
        return 'not interaction'


interaction = Interaction()


########################################################################################################################


class Length(BaseCondition):
    """ Ожидлание размера списка элементов """

    def __init__(self, ln):
        self.ln = ln

    def identity(self):
        return 'elements'

    def apply(self):
        return len(self.driver) == self.ln

    # def expected(self):
    #     return 'interaction'
    #
    # def actual(self):
    #     return 'not interaction'


def length(ln):
    return Length(ln)
