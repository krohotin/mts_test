import unittest
import logging

from selenium.common.exceptions import NoSuchElementException

from lib.core.finder import s, ss
from lib.core.tools import get, refresh, title, close
from lib.core.driver import replace_current_driver
from selenium import webdriver


# Примитивный способ настроить взаимодействие с драйвером - прописать путь до него
browser = webdriver.Chrome("C:\\chromedriver.exe")
browser.maximize_window()
replace_current_driver(browser)


logging.basicConfig(filename="sample.log", format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = logging.INFO)


def info(message):
    logging.info(message)


class WorkTest(unittest.TestCase):

    def open_page(self):
        """ открываем начальную страницу """
        info("Открываем страницу по ссылке  \"" + self.base_url + " \"")
        get(self.base_url)
        info("Осуществлен переход на страницу \"" + title() + "\"")

    def open_section(self):
        """Открываем раздел 'Системные блоки'. Структура переходов немного отличается от описанного в тестовом
        задании, т.к. описанной структуры переходов на сайте не видел (видимо устарела задача или поменяли сайт) """
        s(text="Компьютеры").click()
        info("Осуществлен переход на страницу \"" + title() + "\"")
        s(text="Компьютеры, ноутбуки и ПО").click()
        info("Осуществлен переход на страницу \"" + title() + "\"")
        s(text="Системные блоки").click()
        info("Осуществлен переход на страницу \"" + title() + "\"")

    def set_sort(self, text):
        """ Выбираем как сортировать """
        _text = text.lower()
        if not s(xpath_text="Сортировать:").s(xpath="..").s(class_name="top-filter__selected").text == _text:
            s(xpath_text="Сортировать:").s(xpath="..").s(class_name="top-filter__selected").click()
            s(xpath_text=text).click()
            refresh()
        self.assertEqual(s(xpath_text="Сортировать:").s(xpath="..").s(class_name="top-filter__selected").text, _text)
        info("Выбран способ сортировки \n" + text + "\n")

    def open_product_by_number(self, number):
        """ Открываем нужный продукт (по номеру) """
        info("Открываем продукт под индексом " + str(number))
        ss(class_name="product-info__title-link")[number - 1].click()
        info("Осуществлен переход на страницу \"" + title() + "\"")

    def open_product_by_number_from_the_end(self, number):
        """ Открываем нужный продукт (по номеру) с конца """
        info("Открываем продукт под индексом " + str(number) + " с конца")
        p_count = len(ss(class_name="product-info__title-link"))
        p_click_index = p_count - number
        ss(class_name="product-info__title-link")[p_click_index].click()
        info("Осуществлен переход на страницу \"" + title() + "\"")

    def get_test_property(self):
        """ Формируем словарь нужных характеристик, которые ищутся на странице продукта """

        info("Открываем все характеристики продукта")
        self.click_with_href_javascript(s(xpath_text="Все характеристики"))

        info("Собираем параметры продукта...")
        p_dict = {
            "Название": s(class_name="price_item_description").text,
            "Цена": s(class_name="current-price-value").text,
            "Срок гарантии": s(class_name="additional-info-block").ss(tag_name="span")[1].text,
            "ОС": self.get_product_property(" Операционная система "),
            "Модель процессора": self.get_product_property(" Модель процессора "),
            "Количество ядер": self.get_product_property(" Количество ядер процессора "),
            "Тактовая честота": self.get_product_property(" Частота процессора "),
            "Модель дискретной видеокарты": self.get_product_property(" Модель дискретной видеокарты "),
            "Объем видеопамяти": self.get_product_property(" Объем видеопамяти "),
            "Размер оперативной памяти": self.get_product_property(" Размер оперативной памяти "),
            "Тип оперативной памяти": self.get_product_property(" Тип оперативной памяти "),
            "Объем дисков HDD": self.get_product_property(" Суммарный объем жестких дисков (HDD) "),
            "Объем дисков SSD": self.get_product_property(" Объем твердотельного накопителя (SSD) ")
        }
        info("Создан словарь параметров продукта: " + str(p_dict))
        return p_dict

    def last_page_button_click(self):
        """ Клик по кнопке перехода на последнюю страницу """
        info("Кликаем по кнопке перехода на последнюю страницу")
        self.click_with_href_javascript(s(class_name="pagination-widget__page-link_last").s(xpath=".."))
        refresh()  # Обновляю страницу чтобы корректно переопределить и найти элементы

    def get_product_property(self, p_name):
        """ Получаем характеристику продукта по названию характеристики """
        try:
            return s(class_name="options-group").s(xpath_text=p_name).s(xpath="..").s(xpath="..").s(xpath="..").ss(xpath="td")[1].inner_html
        except NoSuchElementException:
            print("Данной характеристики не найдено")

    def click_with_href_javascript(self, element):
        """ Оч костыльный метод клика по элементу element, содержащем в себе параметр href="javascript:". По
        непонятным мне причинам такой элемент иногда кликается с одной попытки, а иногда только со второй. Поэтому
        сделано так криво, но рабоче в рамках тестовой задачи """
        element.click()
        try:
            element.click()
        except:
            pass

    ####################################################################################################################

    def setUp(self):
        """ В данном методе задаем предварительные настройки для теста """
        # Базовый url
        self.base_url = "https://dns-shop.ru/"
        # Индекс - номер открываемого продукта (с начала или с конца)
        # Выставил индекс 1 т.к. в процессе написания теста на сайте уменьшилось кол-во системных блоков, так что на
        # последней странице остался только один блок. Усложнять тест переходом на предыдущую страницу уже счел лишним
        self.p_index = 1

    def tearDown(self):
        # Закрываем браузер
        close()

    ####################################################################################################################

    def test_work(self):
        # П.1 Открывается браузер
        # П.2 Выполняется переход на сайт https://dns-shop.ru/
        self.open_page()

        # П.3 По клику в левом меню выбирается пункт «Компьютеры и периферия» -> «Компьютерные системы» -> «Системные блоки»
        self.open_section()

        # П.4 На странице выбираем сортировку «По убыванию цены»
        self.set_sort("По убыванию цены")

        # П.5 Выбираем нужный продукт в списке, открываем его.
        self.open_product_by_number(self.p_index)

        # П.6 Открываем характеристики продукта и записываем следующую информацию о продукте
        p_dict_1 = self.get_test_property()

        # П.7 Возвращаемся на главную страницу
        self.open_page()

        # П.8 - копия п.3
        self.open_section()

        # П.9 Убеждаемся, что выбрана сортировка «По возрастанию цены», если нет, выбираем
        self.set_sort("По возрастанию цены")

        # П.10 Листаем страницу вниз, жмём кнопку «В конец»
        self.last_page_button_click()

        # П.11 Листаем страницу вниз, выбираем третий снизу продукт, открываем его.
        self.open_product_by_number_from_the_end(self.p_index)

        # П.12 Повторяем п.6
        p_dict_2 = self.get_test_property()

        # Сравниваем характеристики из п.6 и п.12
        info("Сравниваем характеристики продуктов")
        self.assertDictEqual(p_dict_1, p_dict_2)
        info("Сравнение прошло успешно")
