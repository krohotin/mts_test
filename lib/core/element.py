# -*- coding: utf-8 -*-
import io
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from .config import Config
from .finder import s, ss
from .service import Attributes, interaction
from .wait import Wait


def _lazy_element_method(fn):
    """
    Декоратор для методов работы с ленивым элементом.
    Если элемент не загружен, то загружает; если загружен - то использует его.
    Но если при выполнении метода выясняется, что элемент исчез, то ищет его заного и пробует еще раз.
    """
    def wrap(el, *args, **kwargs):
        el.resolve()
        try:
            return fn(el, *args, **kwargs)
        except StaleElementReferenceException as e:
            if el.reload():
                return fn(el, *args, **kwargs)
            else:
                raise e

    return wrap


class Element:
    """Ленивая обертка для selenium'ного элемента"""

    def __init__(self, locator=None, element=None):
        """
        Можно инициализировать либо локатором, либо уже найденым элементом.
        В первом случае элемент можно будет "обновлять" по локатору, во втором - элемент фиксированный.
        """
        if not (locator or element):
            raise ValueError()

        self.locator = locator      # Список локаторов/фильтров/срезов для поиска элемента
        self._element: WebElement = element     # Элемент классического WebElement-а, если есть и/или найден
        self._id = None
        self._refind = False

    def __eq__(self, element):
        """ Сравнение двух элементов """
        self.resolve()
        element.resolve()
        return hasattr(element, '_id') and self._id == element._id

    def __ne__(self, element):
        return not self.__eq__(element)

    def __bool__(self):
        """ Метод bool для проверки, найден ли элемент """
        try:
            self.reload()
            return True
        except:
            return False

    def _javascript(self, script):
        """ Технический метод """
        self.reload()
        script = "return arguments[0].%s;" % script
        return self._element._parent.execute_script(script, self._element)
    
    def reload(self):
        """По локатору перезагружает элемент со страницы """
        if self.locator:
            self._element = self.locator.search()
            self._id = self._element._id
            self._refind = True
            return True
        else:
            return False

    def resolve(self):
        """Загружает элемент, если он еще не загружен"""
        if not self._element:
            self.reload()

    def not_wait(self):
        """ Возвращает элемент, идентичный self, но с нулевым ожиданием всех уровней поиска """
        pass

    def closest_with_class(self, class_name):
        """Возвращает ближайшего родителя с указанным классом"""
        return self.s(xpath='ancestor::*[contains(@class, "%s")]' % class_name)

    @property
    @_lazy_element_method
    def id(self):
        """ Возвращает id элемента """
        return self._id

    @property
    def parent(self):
        """ Возвращает текущий браузер """
        # просто шорткат
        from lib.core import driver
        return driver.current

    @_lazy_element_method
    def unwrap(self):
        """ Врзвращает объект классического WebElenemt-а """
        return self._element

    @property
    @_lazy_element_method
    def refind(self):
        """ Признак - осуществлялся ли перепоиск элемента в случае, например, перезагрузки страницы. Возвращает True
            если перепоиск осуществлялся. При этом скижывает состояние на False, т.к. элемент перенайден и считается
             найденным уже. Альтернатива refind-а - сравнение id элемента, при перепоиске он будет отличаться """
        rez = self._refind
        self._refind = False
        return rez

    def s(self, *args, **kwargs):
        return s(*args, chain=self.locator, **kwargs)

    def ss(self, *args, **kwargs):
        """ Аналогично методу ss() из driver.py """
        return ss(*args, chain=self.locator, **kwargs)

    @_lazy_element_method
    def click(self):
        """ Клик по элементу """
        interaction(self)
        self._element.click()
        return self

    @_lazy_element_method
    def click_on_offset(self, x, y):
        """
        Клик по определенной точке элемента - указывается смещение от левого верхнего угла.
        По факту несколько отличается от обычного click, т.к. там идут некоторые проверки видимости элемента.
        А тут идет просто определение экранных координат и клик по ним.
        """
        ActionChains(self._element._parent).move_to_element_with_offset(self._element, x, y).click().perform()

    @_lazy_element_method
    def mouse_click(self):
        """ Клик мышью по элементу """
        ActionChains(self._element._parent).click(self._element).perform()
        return self

    @_lazy_element_method
    def move_to(self):
        """ Перевод курсора мыши на элемент """
        ActionChains(self._element ._parent).move_to_element(self._element).perform()
        return self

    @_lazy_element_method
    def scroll_to_visible(self):
        """ Скрол страницы до видимости элемента """
        self._element._parent.execute_script('arguments[0].scrollIntoView();', self._element)
        return self

    @_lazy_element_method
    def scroll_by(self, y):
        """ Скрол страницы относительно текущего элемента по оси Y """
        self._element._parent.execute_script("window.scrollBy(0, " + str(y) + ");")
        return self

    @_lazy_element_method
    def write(self, *value):
        """ Ввод значения с клавиатуры """
        interaction(self)
        self._element.send_keys(*value)
        return self

    @_lazy_element_method
    def set(self, text):
        """ Ввод значения с клавиатуры с предварительной очисткой (если например в форме уже были символы) """
        interaction(self)
        self._element.clear()

        if text:
            self._element.send_keys(text)
        else:
            # по крайней мере React не замечает очистку selenium'а, но видит нажатие клавиш
            # так что, хотя поле очищается, генерируем доп. эвенты, что бы клиентский код это заметил
            self._element.send_keys(' ')
            self._element.send_keys(Keys.BACKSPACE)

        return self

    @_lazy_element_method
    def press_enter(self):
        """ Нажатие клавиши ENTER на выбранном элементе """
        self._element.send_keys(Keys.ENTER)
        return self

    @_lazy_element_method
    def press_escape(self):
        """ Нажатие клавиши ESCAPE на выбранном элементе """
        self._element.send_keys(Keys.ESCAPE)
        return self

    @_lazy_element_method
    def clear(self):
        """ Очистка выбранного элемента (например поля ввода от ранее введенных данных) """
        interaction(self)
        self._element.clear()
        return self

    @_lazy_element_method
    def check(self):
        """ Клик по элементу, если у него отсутствует атрибут checked (чекбокс, если не выбран - выберется) """
        interaction(self)
        if not (self._element.get_attribute('checked') is not None):
            self._element.click()
        return self

    @_lazy_element_method
    def uncheck(self):
        """ Клик по элементы, если у него есть атрибут checked (отжать чекбокс) """
        interaction(self)
        if self._element.get_attribute('checked') is not None:
            self._element.click()
        return self

    ####################################################################################################################

    def exist(self):
        """ Проверка, существует ли элемент на странице """
        try:
            self.reload()
            return True
        except:
            return False

    def not_exist(self):
        """ Проверка, существует ли элемент на странице """
        return not self.exist()

    ####################################################################################################################

    @property
    @_lazy_element_method
    def text(self):
        """ Возвращает текст элемена """
        return str(self._element.text)

    @property
    @_lazy_element_method
    def tag_name(self):
        """ Возвращает имя тега элемента """
        return str(self._element.tag_name)

    @property
    @_lazy_element_method
    def html(self):
        """ Возвращает html-код всего элемента (найденный по локаторам тег и его содержимое) """
        script = """
            var container = document.createElement("div");
            container.appendChild(arguments[0].cloneNode(true));
            return container.innerHTML;
        """
        return str(self._element._parent.execute_script(script, self._element))

    @property
    @_lazy_element_method
    def inner_html(self):
        """ Возвращает htmt-код который находится ВНУТРИ элемента """
        return str(self._element.get_attribute('innerHTML'))

    @property
    def tag_html(self):
        """ Возвращает html-код верхнего тега найденного элемента (содержащий искомый локатор) """
        return str(self.html[:self.html.find('>')+1])

    @property
    @_lazy_element_method
    def size(self):
        """ Возвращает список - размер элемента """
        val = self._element.size
        return [val['width'], val['height']]

    @property
    @_lazy_element_method
    def area(self):
        """ Площадь элемента """
        [w, h] = self.size
        return w * h

    @property
    @_lazy_element_method
    def location(self):
        """ Возвращает список с координатами элемента """
        return [self._element.location['x'], self._element.location['y']]

    @property
    def x(self):
        """ х-коорината элемента """
        return int(self._element.location['x'])

    @property
    @_lazy_element_method
    def y(self):
        """ у-координата элемента """
        return int(self._element.location['y'])

    @_lazy_element_method
    def value(self):
        """ Возвращает значение атрибута value """
        return str(self._element.get_attribute('value'))

    @_lazy_element_method
    def attr_dict(self):
        """ Возвращает словарь атрибутов элемента """
        z = {}
        z.update(Attributes(self._element)._get_attributes())
        return z

    @_lazy_element_method
    def attr(self, name):
        """ Возвращает заданный атрибут элемента """
        return self._element.get_attribute(name)

    @_lazy_element_method
    def attr_add(self, **kwargs):
        """ Добавляет/заменяет атрибуты элемента и возвращает новый словарь """
        if len(kwargs) == 0:
            pass
        else:
            from .service import Attributes
            for arg, value in kwargs.items():
                Attributes(self._element)[str(arg)] = str(value)
        z = {}
        z.update(Attributes(self._element)._get_attributes())
        return z

    @_lazy_element_method
    def attr_del(self, *args):
        """ Удаляет атрибуты элемента и возвращает новый словарь """
        from .service import Attributes
        for i in args:
            Attributes(self._element).__delitem__(i)
        z = {}
        z.update(Attributes(self._element)._get_attributes())
        return z

    @_lazy_element_method
    def css(self, value):
        """ Возвращает значение выбранного css-свойства объекта """
        return str(self._element.value_of_css_property(str(value)))

    # is_ - булевы проверки свойств элемента ###########################################################################

    @_lazy_element_method
    def is_displayed(self):
        """ Виден ли элемент на дисплее """
        return self._element.is_displayed()

    @_lazy_element_method
    def is_visible(self):
        """ Виден ли элемент на дисплее и его размеры не должны равняться нулю """
        return self.is_displayed() and self.area > 0

    @_lazy_element_method
    def is_enabled(self):
        """ Доступен ли элемент для взаимодействия """
        return self._element.is_enabled()

    @_lazy_element_method
    def is_interaction(self):
        """ Доступен ли элемент для взаимодействия и является ли он видимым для пользователя """
        return self.is_visible() and self.is_enabled()

    @_lazy_element_method
    def is_selected(self):
        """ Выбран ли элемент """
        return self._element.is_selected()

    @_lazy_element_method
    def is_check(self):
        """ Чекнут ли элемент """
        return bool(self._element.get_attribute('checked'))

    @_lazy_element_method
    def is_text(self, txt):
        """ Содержит ли элемент текст """
        return self.text == txt

    def is_not_visible(self):
        """ Отсутствует ли элемент на странице или элемент невидим """
        if self.exist():
            if self.is_visible():
                return False
        return True

    @_lazy_element_method
    def is_partial_text(self, txt):
        """ Содержит ли элемент текст """
        return txt in self.text

    @_lazy_element_method
    def is_attr(self, attr):
        """ Содержит ди элемент атрибут """
        return self.attr(attr) is not None

    @_lazy_element_method
    def is_value(self, vl):
        """ Равно ли значение value элемента переданному """
        return bool(vl == self.value())

    @_lazy_element_method
    def is_css_property(self, prop):
        """ Имеет ли элемент css-войство """
        return bool(self.css(prop) == "")

    # wait_ - ожидания, оканчиваются TimeoutException ##################################################################

    @_lazy_element_method
    def wait(self, condition, message="", wait=Config.wait_timeout, pool=Config.pool_frequency):
        """ Базовое ожидание """
        message = message if message != "" else condition
        Wait(self, wait, pool).until(condition, message)
        return self
