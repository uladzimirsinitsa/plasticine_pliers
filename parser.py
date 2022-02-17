
from datetime import datetime
from bs4 import BeautifulSoup
import re

URL = 'https://boxrec.com'


def get_file():
    with open(r'C:\data\data\9625', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def get_soup(text):
    return BeautifulSoup(text, 'lxml')


def get_all_fights_statistics(soup) -> dict[str, int]:
    return {
        'number_fight_win': int(soup.find(class_='bgW').text),
        'number_fight_loose': int(soup.find(class_='bgL').text),
        'number_fight_draw': int(soup.find(class_='bgD').text)
        }


def get_date_career(soup):
    profile = soup.find(class_='profileTable').find('table', class_='rowTable').find_all('tr')
    data = {}
    for item in profile[1:]:
        item = item.find_all('td')
        data[item[0].text.strip()] = item[1].text.strip()
    return {
        'start': datetime.strptime(data['career'].split('-')[0], '%Y'),
        'end': datetime.strptime(data['career'].split('-')[1], '%Y'),
        }


def get_profile(soup) -> tuple[str, dict]:
    obj_beautifulsoup = soup.find(class_='profileTable').find_all('table')[2].find_all('tr')
    list_obj_beautifulsoup = [item.find_all('td') for item in obj_beautifulsoup]
    dict_obj_beautifulsoup = {
        item[0].text.strip(): item[1].text.strip()
        for item in list_obj_beautifulsoup
        if item
    }
    name = soup.find_all('h1')[1].text
    return name, {
        'name': name,
        'age': {},
        'height': int(dict_obj_beautifulsoup['height'][-6:-2]),
        'reach': int(dict_obj_beautifulsoup['reach'][-6:-2]),
        'residence': dict_obj_beautifulsoup['residence'],
        'birth place': dict_obj_beautifulsoup['birth place'],
        'alias': dict_obj_beautifulsoup['alias'],
        'stance': dict_obj_beautifulsoup['stance'] or {},
        'nationality': dict_obj_beautifulsoup['nationality']
        }

def get_opponent_data(soup):
    opponent_name = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(class_='personLink', href=re.compile(r'/en/proboxer/')).text
    opponent_link = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(class_='personLink', href=re.compile(r'/en/proboxer/')).get('href')
    return opponent_name, {'opponent': {'name': opponent_name, 'link': f'{URL}{opponent_link}'}}


def get_fight_data(soup, name):
    obj_beautifulsoup = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find_all('td')

    values = [item.text.replace('\n', '').strip() for item in obj_beautifulsoup]
    print(values[11])
    kilos, rating = values[2:4]

    result =soup.find(class_='boutResult bgW').text
    if result=='W':
        result = 1
    elif result=='L':
        result = 0
    elif result=='D':
        result = 0.5
    else:
        result = {}

    fight_data = {
        'date': datetime.strptime(soup.find(href=re.compile(r'date=')).text, '%Y-%m-%d'),
        'kilos': kilos,
        'rating': rating,
        'rounds': 'rounds',
        'result': result,
    }
    return fight_data

def create_dict_referee_and_judges(soup, name, opponent_name):
    print(opponent_name)
    list_judges = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find_all(href=re.compile(r'/en/judge/'))
    judges = {}
    for item in list_judges:
        score = re.search(r'([0-9]+)-([0-9]+)', item.next.next.strip())
        judges[f'{item.text}'] = {'judges_link': f'{URL}{item.get("href")}', 'score': {name: int(score.group(1)), opponent_name: int(score.group(2))} }
    referee_name = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(href=re.compile(r'/en/referee/')).text
    referre_link = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(href=re.compile(r'/en/referee/')).get('href')
    referee = {'name': referee_name, 'referee_link': f'{URL}{referre_link}'}

    return {
        'referee': referee,
        'judges': judges
        }


def main():
    text = get_file()
    soup = get_soup(text)
    statistics = get_all_fights_statistics(soup)
    career_length = get_date_career(soup)
    name, profile = get_profile(soup)
    fights_records = get_fight_data(soup, name)
    opponent_name, opponent_data = get_opponent_data(soup)
    referee_and_judges = create_dict_referee_and_judges(soup, name, opponent_name)


if __name__=='__main__':
    main()
