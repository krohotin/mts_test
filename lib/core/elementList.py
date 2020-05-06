# -*- coding: utf-8 -*-
from .element import Element
from .finder import Locator


class ElementList(list):
    """
    Список элементов.

    По факту совесем даже не список, больше обертка над локатором.
    На каждое действие перезапрашивает элементы.
    """

    def __init__(self, locator):
        super().__init__()
        self.locator = locator

    def __bool__(self):
        return len(self) > 0

    def __len__(self):
        return len(self.locator.search())

    def __getitem__(self, item):
        if isinstance(item, slice):
            locator = Locator('slice', slice=item, chain=self.locator)
            return ElementList(locator)
        else:
            locator = Locator('slice int', slice=item, chain=self.locator)
            return Element(locator)

    def __iter__(self):
        for el in self.locator.search():
            yield Element(None, element=el)

    def unwrap(self):
        """ Возвращает список классических элементов WebDriver-а """
        return self.locator.search()

    # @property
    # def text(self):
    #     """ Возвращает тексты всех найденных элементов """
    #     return [el.text for el in self]

    def is_visible_list(self):
        return [el.is_visible() for el in self]

    def is_interaction_list(self):
        return [el.is_interaction() for el in self]

    def all_visible(self):
        return self.is_visible_list().count(False) == 0

    def all_interaction(self):
        return self.is_interaction_list().count(False) == 0

    # FIXME нахрена?
    # TODO в test_case для проверок assertElementVisible и assertElementInteraction (у элемента и у списка элементов делает одинаковое название метода)
    is_visible = all_visible
    is_interaction = all_interaction
