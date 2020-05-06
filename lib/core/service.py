# -*- coding: utf-8 -*-
# Набор воспомогательных функций и классов, вынесенных в отдельный модуль

from .config import Config
from .wait import Wait


def correct_url(url):
    """ Приведение url-а к виду, воспринимаемому webdriver-ом """
    if len(Config.base_url) == 0:
        pass
    else:
        if url == "":
            url = Config.base_url
        elif Config.base_url[-1] == url[0] == "/":
            url = Config.base_url + url[1:]
        elif Config.base_url[-1] != "/" and url[0] != "/":
            url = Config.base_url + "/" + url
        else:
            url = Config.base_url + url
    url = "https://" + url if url.find("https://") < 0 and url.find("http://") < 0 else url
    return url


def interaction(ob, wait=Config.wait_timeout):
    """ Ожидание интерактивности элемента """
    Wait(ob, wait).bool(lambda dd: dd.is_interaction())


class Attributes(object):
    """
    Allows getting, setting and deleting attributes.
    """

    def __init__(self, elem):
        self._elem = elem

    def _get_attributes(self):
        script = """
        var elem = arguments[0];
        var ret = {}
        for (var i=0, attrs=elem.attributes, l=attrs.length; i<l; i++){
            ret[attrs.item(i).nodeName] = attrs.item(i).nodeValue
        }
        return ret"""
        return self._elem._parent.execute_script(script, self._elem)

    def __getitem__(self, name):
        from ..core.element import Element
        return Element("", self._elem)._javascript("getAttribute('%s')" % name)

    def __setitem__(self, name, value):
        from ..core.element import Element
        return Element("", self._elem)._javascript("setAttribute('%s', %s)" % (name, repr(value)))

    def __delitem__(self, name):
        from ..core.element import Element
        return Element("", self._elem)._javascript("removeAttribute('%s')" % name)

    def __getattr__(self, name):
        data = self._get_attributes()
        return getattr(data, name)

    def __repr__(self):
        return repr(self._get_attributes())

    def __eq__(self, other):
        return self._get_attributes() == other
