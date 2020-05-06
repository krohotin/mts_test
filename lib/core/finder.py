# -*- coding: utf-8 -*-
# Модуль отвечающий за поиск элементов
# from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .config import Config


def s(*args, chain=None, **kwargs):
    """
        Ленивый поисковик элементов на странице.
        Поиск осуществляется при выполнении действия (клик, ввод данных, и т.п.), получения
        свойств (видимость, размер, координаты, и т.п.), или использовании метода find(). В качестве параметров
        метод может применять:

            именованные параметры. Например, передав именованный параметр href="/app/common/Login/", мы инициируем
            поиск элемента с соответствующим параметром. Список поддерживаемых параметров: id, id_contains, xpath,
            name, tag_name, class_value, class_name, css, text, link_text_contains, attr, text_contains, value,
            type, checked, selected, href, button, а так же wait (время поиска элемента). Прочие именованные
            параметры автоматически формируют поиск аттрибута с таким названием

            аргументы типа str. В таком случае они считаются css селекторами

        С помощью этого метода можно строить цепочку поиска с последующим действием, например
        s(Be.name("email)).s(href="/app/common/Login/").s("condision").click(). В случае ненахождения какого-либо
        элемента метод возбуждает исключение классического WebDriver-а
    """
    from .element import Element

    wait = kwargs.pop('wait', Config.wait_timeout)
    locator = Locator("s", (args, kwargs), wait, './/*', chain=chain)
    return Element(locator=locator)


def ss(*args, chain=None, **kwargs):
    """
        Аналогия метода s(), с той разницей что возвращает список элементов, а не первый найденный элемент. В случае
        ненахождения элемента возвращает пустой список. Включает дополнительные параметры filter (передается метод,
        по которому можно отфильтровать элементы списка, например видимость) и size (ожидаемый размер списка, если
        размер не совпадает - будет возбуждено исключение)
    """
    from .elementList import ElementList

    wait = kwargs.pop('wait', Config.wait_timeout)
    _filter = kwargs.pop('filter', None)
    _size = kwargs.pop('size', None)

    locator = Locator('ss', (args, kwargs), wait, '//*', _filter, _size, chain=chain)
    return ElementList(locator)


class InvalidSizeList(BaseException):
    """ Ошибка когда размер списка элементов не равен заданному """
    pass


def xpath_literal(s):
    """ Вспомогательный метод формирования xpath-а"""
    if "'" not in s:
        return "'%s'" % s
    if '"' not in s:
        return '"%s"' % s
    return "concat('%s')" % s.replace("'", "',\"'\",'")


def _list_common_elements(list1, list2):
    """ Сравнение двух списков и формирование списка, состоящего из неповторяющихся элементов обоих списков """
    # если не пустой только один, то возвращаем второй
    if not(list1 and list2):
        return list1 or list2 or []

    common = []
    for i1 in list1:
        for i2 in list2:
            if i2.id == i1.id:
                common.append(i2)
    res = []
    for item in common:
        if item not in res:
            res.append(item)
    return res


__ARG_TO_SELECTOR__ = {
    'id':
        lambda _xpath_prefix, val: (By.ID, val),
    'id_contains':
        lambda _xpath_prefix, val: (By.XPATH, '%s[contains(@id, %s)]' % (_xpath_prefix, xpath_literal(val))),
    'xpath':
        lambda _xpath_prefix, val: (By.XPATH, val),
    'name':
        lambda _xpath_prefix, val: (By.NAME, val),
    'tag_name':
        lambda _xpath_prefix, val: (By.TAG_NAME, val),
    'class_value':
        lambda _xpath_prefix, val: (By.XPATH, '%s[@class=%s]' % (_xpath_prefix, xpath_literal(val))),
    'class_name':
        lambda _xpath_prefix, val: (By.CLASS_NAME, val),
    'css':
        lambda _xpath_prefix, val: (By.CSS_SELECTOR, val),
    'text':
        lambda _xpath_prefix, val: (By.LINK_TEXT, val),
    'partial_link_text':
        lambda _xpath_prefix, val: (By.PARTIAL_LINK_TEXT, val),
    'attr':
        lambda _xpath_prefix, val: (By.XPATH, '%s[@%s]' % (_xpath_prefix, val)),
    'xpath_text':
        lambda _xpath_prefix, val: (By.XPATH,
                                    '%s[text()=%s]' % (_xpath_prefix, xpath_literal(val))),
    'text_contains':
        lambda _xpath_prefix, val: (By.XPATH,
                                    '%s/text()[contains(.,%s)]/..' % (_xpath_prefix, xpath_literal(val))),
    'value':
        lambda _xpath_prefix, val: (By.XPATH,
                                    '%s[@value=%s]' % (_xpath_prefix, xpath_literal(val))),
    'type':
        lambda _xpath_prefix, val: (By.XPATH,
                                    '%s[@type=%s]' % (_xpath_prefix, xpath_literal(val))),
    'checked':
        lambda _xpath_prefix, val: (By.XPATH,
                                    _xpath_prefix + ('[@checked]' if val else '[not(@checked)]')),
    'selected':
        lambda _xpath_prefix, val: (By.XPATH,
                                    _xpath_prefix + ('[@selected]' if val else '[not(@selected)]')),
    'href':
        lambda _xpath_prefix, val: (By.XPATH, '%s[@href=%s]' % (_xpath_prefix, xpath_literal(val))),
    'button':
        lambda _xpath_prefix, value: (By.XPATH, "%sinput[@type='submit' or @type='button' and @value='{0}']"
                                                 "|%sbutton[text()=%s]" % (_xpath_prefix, _xpath_prefix, value)),
    # Отказались от attribute_value, сохранено как шаблон
    'attribute_value':
        lambda _xpath_prefix, val: (By.XPATH,
                                    '%s[@%s=%s]' % (_xpath_prefix, val[0], xpath_literal(val[1])))
}


def _get_selector(_xpath_prefix, locator_type, locator):
    """ Получение конечного локатора для поиска элемента """
    func = __ARG_TO_SELECTOR__.get(locator_type, None)
    if func:
        end_locator = func(_xpath_prefix, locator)
    else:
        func = __ARG_TO_SELECTOR__.get('attribute_value', None)
        end_locator = func(_xpath_prefix, (locator_type, locator))
    return end_locator


class Locator:
    """ Класс локатора """

    def __init__(self, operation_type, args=None, wait=None, xpath_prefix=None, filter_method=None, size=None, slice=None, chain=None):
        """
            Объект класса Locator со следующими св-ми:
                operation_type - тип операции
                locator_list - список локаторов (словари {'type': тип_локатора , 'value': значение_локатора})
                wait - ожидание элемента
                xpath_prefix - xpath-префикс
                filter_method - метод фильтрации (для списка элементов)
                size - размер списка (для списка элементов)
                slice - срез (для списка элементов)
        """
        self.operation_type = operation_type        # Тип операции (s, ss, ss_s, slice, slice_int, filter)
        self.locator_list = self._parse_args(args)  # Список объектов-локаторов
        self.wait = wait                            # Ожидание
        self.xpath_prefix = xpath_prefix            # xpath prefix
        self.filter_fn = filter_method          # Метод фильтрации
        self.size = size                            # Размер списка
        self.slice = slice                          # срез
        self.chain = chain  # предыдущий локатор

        # особый переход ss -> s
        if self.chain and self.operation_type == 's' and self.chain.operation_type == 'ss':
            self.operation_type = 'ss_s'

    def chain(self, *args, **kwargs):
        return Locator(*args, chain=self, **kwargs)

    def search(self):
        """Поиск элементов по локаторам"""
        from .wait import Wait
        from ..core import driver
        
        if self.chain:
            target = self.chain.search()
        else:
            target = driver.current

        if self.operation_type == 's':
            Wait(target, self.wait).bool(lambda dd: self._find_first(target))
            return self._find_first(target)
        elif self.operation_type == 'ss':
            Wait(target, self.wait).bool(lambda dd: self._find_first(target))
            if not self.size:
                rz = self._find_all(target)
            else:
                _ = Wait(target).bool(lambda _: len(self._find_all(target)) == self.size)
                if not _:
                    raise InvalidSizeList(
                        "length of the elements list does not equal %s, and equal to %s " % 
                        (self.size, len(self._find_all(target)))
                    )
                rz = self._find_all(target)
                
            if self.filter_fn:
                rz = self._apply_filter_fn(rz)
            return rz
        elif self.operation_type == 'ss_s':
            rz = []
            for el in target:
                Wait(el, self.wait).bool(lambda dd: self._find_first(el))
                rz.append(self._find_first(el))
            return rz
        # TODO это точно надо?
        elif self.operation_type == "slice" or self.operation_type == "slice int":
            return target[self.slice]
        elif self.operation_type == "filter":
            return self._apply_filter_fn(target)
        else:
            raise ValueError(self.operation_type)

    def _apply_filter_fn(self, items):
        """Применяет фильтр локатора в виде функции"""
        from ..core.element import Element

        if self.filter_fn:
            return [v for v in items if self.filter_fn(Element("", v))]
        else:
            return items

    def _find_first(self, base):
        """ Ф-я поиска элемента по списку локаторов """
        elements = None
        for locator in self.locator_list:
            by, value = _get_selector(self.xpath_prefix, locator['type'], locator['value'])
            found = base.find_elements(by=by, value=value)

            if not found:
                # raise NoSuchElementException("Unable to locate element:")
                # FIXME вернул поиск одного элемента, выдает более полную информацию о том какой элемент не найден
                base.find_element(by=by, value=value)

            elements = _list_common_elements(elements, found)

        return elements[0]

    def _find_all(self, base):
        """ Ф-я поиска элементов по списку локаторов """
        elements = None
        for locator in self.locator_list:
            by, value = _get_selector(self.xpath_prefix, locator['type'], locator['value'])
            found = base.find_elements(by=by, value=value)
            elements = _list_common_elements(elements, found)

        return elements

    def _parse_args(self, args):
        if not args:
            return []
        else:
            args, kwargs = args
            return [{'type': 'css', 'value': v} for v in args] + [{'type': k, 'value': v} for k, v in kwargs.items()]
