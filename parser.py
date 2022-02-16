
from datetime import datetime
from bs4 import BeautifulSoup
import re

def get_file():
    with open(r'C:\data\data\432984', 'r', encoding='utf-8') as file:
        text = file.read()
    return text


def get_profile(text):
    soup = BeautifulSoup(text, 'lxml')

    name = soup.find_all('h1')
    name = name[1].text

    number_fight_win = soup.find(class_='bgW').text
    number_fight_loose = soup.find(class_='bgL').text
    number_fight_draw = soup.find(class_='bgD').text

    profile = soup.find(class_='profileTable').find('table', class_='rowTable').find_all('tr')

    data = {}
    for item in profile[1:]:
        item = item.find_all('td')
        data[item[0].text.strip()] = item[1].text.strip()

    start = datetime.strptime(data['career'].split('-')[0], '%Y')
    end = datetime.strptime(data['career'].split('-')[1], '%Y')
    how_long = {'start': start, 'end': end}
    debut = datetime.strptime(data['debut'], '%Y-%m-%d')
    naming = soup.find(class_='profileTable').find_all('table')[2].find_all('tr')

    list_naming = [item.find_all('td') for item in naming]
    dict_naming = {
        item[0].text.strip(): item[1].text.strip()
        for item in list_naming
        if item
    }

    alias = dict_naming['alias']
    nationality = dict_naming['nationality']
    height = int(dict_naming['height'][-6:-2])
    reach = int(dict_naming['reach'][-6:-2])
    stance = dict_naming['stance']
    residence = dict_naming['residence']
    birth = dict_naming['birth place']

    return {
        'name': name,
        'age': {},
        'height': height,
        'reach': reach,
        'residence': residence,
        'birth place': birth,
        'number_fight_win': int(number_fight_win),
        'number_fight_loose': int(number_fight_loose),
        'number_fight_draw': int(number_fight_draw),
        'division': data['division'],
        'bouts': int(data['bouts']),
        'rounds': int(data['rounds']),
        'KOs': float(data['KOs'].strip('%')),
        'career': how_long,
        'debut': debut,
        'alias': alias,
        'stance': stance or {},
        'nationality': nationality
        }

def get_records(text):
    soup = BeautifulSoup(text, 'lxml')
    raw_data = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find_all('td')


    keys = ['date', 'kilos', 'rating', 'opponent', 'kilos', 'rating', ['w', 'l', 'd'], 'last 6', 'result', 'rounds']
    


    values = []
    for item in raw_data:
        values.append(item.text.replace('\n', '').strip())


    date = soup.find(href=re.compile(r'date=')).text
    date = datetime.strptime(date, '%Y-%m-%d')

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

    opponent_name = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(class_='personLink', href=re.compile(r'/en/proboxer/')).text
    opponent_link = soup.find(class_='dataTable', align='center').find_all('tbody')[0].find(class_='personLink', href=re.compile(r'/en/proboxer/')).get('href')
    opponent = {'name': opponent_name, 'link': f'https://boxrec.com/{opponent_link}'}
    #judges = values.pop()

    print(values)

    with open('file', 'w', encoding='UTF-8') as file:
        file.write(str(raw_data))


    records = {
        'date': date,
        'kilos': kilos,
        'rating': rating,
        'result': result,
        'opponent': opponent
    }

    
    return records



def main():
    text = get_file()
    profile = get_profile(text)
    records = get_records(text)
    print('\n')
    print(records)



if __name__=='__main__':
    main()
