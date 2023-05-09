# _____ЗАДАНИЕ 1_____
import os
from datetime import datetime


def logger(old_function):
    def new_function(*args, **kwargs):
        result = old_function(*args, **kwargs)

        with open('main.log', 'a') as f:
            f.write(f'{datetime.now()} - {old_function.__name__} - args: {args}, kwargs: {kwargs}, result: {result}\n')

        return result

    return new_function


def test_1():
    path = 'main.log'
    if os.path.exists(path):
        os.remove(path)

    @logger
    def hello_world():
        return 'Hello World'

    @logger
    def summator(a, b=0):
        return a + b

    @logger
    def div(a, b):
        return a / b

    assert 'Hello World' == hello_world(), "Функция возвращает 'Hello World'"
    result = summator(2, 2)
    assert isinstance(result, int), 'Должно вернуться целое число'
    assert result == 4, '2 + 2 = 4'
    result = div(6, 2)
    assert result == 3, '6 / 2 = 3'

    assert os.path.exists(path), 'файл main.log должен существовать'

    summator(4.3, b=2.2)
    summator(a=0, b=0)

    with open(path) as log_file:
        log_file_content = log_file.read()

    assert 'summator' in log_file_content, 'должно записаться имя функции'
    for item in (4.3, 2.2, 6.5):
        assert str(item) in log_file_content, f'{item} должен быть записан в файл'


if __name__ == '__main__':
    test_1()

# _____ЗАДАНИЕ 2_____
import os
import datetime


def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            with open(path, 'a') as f:
                f.write(
                    f'{datetime.datetime.now()} вызов функции {old_function.__name__} с аргументами {args}, {kwargs}\n')
            result = old_function(*args, **kwargs)
            with open(path, 'a') as f:
                f.write(f'{datetime.datetime.now()} функция {old_function.__name__} возвращает {result}\n')
            return result

        return new_function

    return __logger


def test_2():
    paths = ('log_1.log', 'log_2.log', 'log_3.log')

    for path in paths:
        if os.path.exists(path):
            os.remove(path)

        @logger(path)
        def hello_world():
            return 'Hello World'

        @logger(path)
        def summator(a, b=0):
            return a + b

        @logger(path)
        def div(a, b):
            return a / b

        assert 'Hello World' == hello_world(), "Функция возвращает 'Hello World'"
        result = summator(2, 2)
        assert isinstance(result, int), 'Должно вернуться целое число'
        assert result == 4, '2 + 2 = 4'
        result = div(6, 2)
        assert result == 3, '6 / 2 = 3'
        summator(4.3, b=2.2)

    for path in paths:

        assert os.path.exists(path), f'файл {path} должен существовать'

        with open(path) as log_file:
            log_file_content = log_file.read()

        assert 'summator' in log_file_content, 'должно записаться имя функции'

        for item in (4.3, 2.2, 6.5):
            assert str(item) in log_file_content, f'{item} должен быть записан в файл'


if __name__ == '__main__':
    test_2()

# _____ЗАДАНИЕ 3_____
import time
import json
from datetime import datetime
import requests
from fake_headers import Headers
from bs4 import BeautifulSoup

HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'

vacancies = []


def logger(old_function):
    def new_function(*args, **kwargs):
        result = old_function(*args, **kwargs)

        with open('vacancy_log.log', 'a', encoding='utf-8') as f:
            f.write(f'{datetime.now()} - {old_function.__name__} - args: {args}, kwargs: {kwargs}, result: {result}\n')

        return result

    return new_function


@logger
def get_headers():
    return Headers(browser='chrome', os='win').generate()


@logger
def get_info_of_vacancy(href, city):
    search_param = ['Django', 'Джанго', 'Flask', 'Фласк']
    vacancy_info = []
    vacancy_page = requests.get(href, headers=get_headers())
    soup = BeautifulSoup(vacancy_page.text, 'lxml')
    vacancy_description = soup.find('div', {'class': 'vacancy-section'}).text
    for p in search_param:
        if p in vacancy_description:
            vacancy_title = soup.find('h1', {'class': 'bloko-header-section-1', 'data-qa': 'vacancy-title'}).text
            vacancy_info.append(vacancy_title)
            vacancy_info.append(city)
            vacancy_salary = soup.find('div', {'data-qa': 'vacancy-salary'}).find('span', {
                'class': 'bloko-header-section-2 bloko-header-section-2_lite'}).text
            vacancy_info.append(vacancy_salary)
            company_element = soup.find('div', {'class': 'vacancy-company-details'})
            company_name = company_element.find('span', {'class': 'vacancy-company-name'}).text.strip()
            vacancy_info.append(company_name)
            vacancy_info.append(href)
            vacancy_info[2] = vacancy_info[2].replace('\xa0', ' ')
            vacancy_info[3] = vacancy_info[3].replace('\xa0', ' ')
            return vacancy_info
    time.sleep(2)


@logger
def create_json(date):
    vacancy_dict = {
        'vacancy_title': date[0],
        'city': date[1],
        'vacancy_salary': date[2],
        'company_name': date[3],
        'href': date[4]
    }
    vacancies.append(vacancy_dict)

    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(vacancies, f, ensure_ascii=False, indent=4)


search_page = requests.get(HOST, headers=get_headers())
soup = BeautifulSoup(search_page.text, 'lxml')
all_vacancy = soup.findAll('div', class_='vacancy-serp-item__layout')

for vacancy in all_vacancy:
    vacancy_city = vacancy.find('div', {'class': 'bloko-text',
                                        'data-qa': 'vacancy-serp__vacancy-address'}).text.split(', ')[0]
    first_href = vacancy.find('a')['href']
    info_of_vacancy = get_info_of_vacancy(first_href, vacancy_city)
    if info_of_vacancy:
        create_json(info_of_vacancy)
    time.sleep(2)
