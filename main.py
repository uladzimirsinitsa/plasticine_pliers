
import os
import re
import pickle
import time
from datetime import datetime
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


PATH_DRIVER = os.environ['PATH_DRIVER']
URL = os.environ['URL']
DOMAIN = os.environ['DOMAIN']


service = Service(PATH_DRIVER)
driver = webdriver.Firefox(service=service)
driver.get(URL)
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)


def get_file() -> list:
    with open(r'C:\data\data\9625', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def get_soups(text: list) -> list:
    soup = BeautifulSoup(text, 'lxml')
    soups = [soup]
    number = int(soup.find_all(class_='pagerElement')[-1].text)
    url = soup.find(rel='canonical').get('href')
    page_ID = 100
    while number > 0 and soup.find_all(class_='pagerElement'):
        driver.get(f'{url}?offset={page_ID}')
        soups.append(BeautifulSoup(driver.page_source, 'lxml'))
        number -= 1
        page_ID += 100
        time.sleep(2)
    return soups


def get_all_fights_statistics(soups: list) -> dict[str, int]:
    return {
        'number_fight_win': int(soups[0].find(class_='bgW').text),
        'number_fight_loose': int(soups[0].find(class_='bgL').text),
        'number_fight_draw': int(soups[0].find(class_='bgD').text)
        }


def get_date_career(soups: list):
    profile = soups[0].find(class_='profileTable').find('table', class_='rowTable').find_all('tr')
    data = {}
    for element in profile[1:]:
        element = element.find_all('td')
        data[element[0].text.strip()] = element[1].text.strip()
    return {
        'start': datetime.strptime(data['career'].split('-')[0], '%Y'),
        'end': datetime.strptime(data['career'].split('-')[1], '%Y'),
        }


def get_profile(soups: list) -> tuple[str, dict]:
    obj_beautifulsoup = soups[0].find(class_='profileTable').find_all('table')[2].find_all('tr')
    list_obj_beautifulsoup = [element.find_all('td') for element in obj_beautifulsoup]
    dict_obj_beautifulsoup = {
        element[0].text.strip(): element[1].text.strip()
        for element in list_obj_beautifulsoup
        if element
    }
    name = soups[0].find_all('h1')[1].text

    return name, {
        "name": name,
        "age": None,
        "height": int(dict_obj_beautifulsoup['height'][-6:-2]),
        "reach": int(dict_obj_beautifulsoup['reach'][-6:-2]),
        "residence": dict_obj_beautifulsoup.get('residence'),
        "birth place": dict_obj_beautifulsoup.get('birth place'),
        "alias": dict_obj_beautifulsoup.get('alias'),
        "stance": dict_obj_beautifulsoup.get('stance'),
        "nationality": dict_obj_beautifulsoup.get('nationality'),
    }


def get_opponent_data(element):
    opponent_name = element.find(class_='personLink', href=re.compile(r'/en/proboxer/')).text
    link = element.find(class_='personLink', href=re.compile(r'/en/proboxer/')).get('href')
    return opponent_name, {'name': opponent_name, 'link': f'{URL}{link}'}


def get_fight_data(soup, element):
    obj_beautifulsoup = element.find_all('td')
    values = [element.text.replace('\n', '').strip() for element in obj_beautifulsoup]
    kilos, rating = values[2:4]

    result =soup.find(class_='boutResult bgW').text
    if result=='W':
        result = 1
    elif result=='L':
        result = 0
    elif result=='D':
        result = 0.5
    else:
        result = None

    return {
        "date": datetime.strptime(
            soup.find(href=re.compile(r'date=')).text, '%Y-%m-%d'
        ),
        "kilos": kilos,
        "rating": rating,
        "rounds": values[11],
        "result": result,
    }


def create_dict_referee_and_judges(soup, name, opponent_name):
    list_judges = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find_all(href=re.compile(r'/en/judge/'))
    judges = {}
    for element in list_judges:
        score = re.search(r'([0-9]+)-([0-9]+)', element.next.next.strip())
        judges[f'{element.text}'] = {'judges_link': f'{URL}{element.get("href")}', 'score': {name: int(score.group(1)), opponent_name: int(score.group(2))} }
    referee_name = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(href=re.compile(r'/en/referee/')).text
    referre_link = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(href=re.compile(r'/en/referee/')).get('href')
    referee = {'name': referee_name, 'referee_link': f'{URL}{referre_link}'}

    return {
        "referee": referee,
        "judges": judges
        }


dict_all_fights = {}

def get_parse_all_fights(soups):
    #number = soup.find(rel='canonical').get('href')[31:]
    index = 1
    for soup in soups:
        raw_data = soup.find(class_='dataTable', align='center').find_all('tbody')
        for element in raw_data:
            fight_data = get_fight_data(soups[0], element)
            _, opponent = get_opponent_data(element)
            dict_all_fights[index] = {'opponent': opponent, 'data': fight_data}
            index += 1
    print(dict_all_fights)
    return dict_all_fights


def create_boxer_record():
    pass


def main():
    text = get_file()
    soup = BeautifulSoup(text, 'lxml')
    soups = get_soups(text)
    statistic = get_all_fights_statistics(soups)
    career_length = get_date_career(soups)
    name, profile = get_profile(soups)
    #fights_records = get_fight_data(soup, item)
    opponent_name, opponent_data = get_opponent_data(soup)
    referee_and_judges = create_dict_referee_and_judges(soup, name, opponent_name)
    dict_all_fights = get_parse_all_fights(soups)


if __name__=='__main__':
    main()
