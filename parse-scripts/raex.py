import json
import requests
from parsing.config import FOLDER
from bs4 import BeautifulSoup as BS
import re



YEAR = 2024
HOST = 'https://raex-rr.com'
raex_url = f'{HOST}/education/russian_universities/top-100_universities/{YEAR}/'
page = requests.get(raex_url)

html = BS(page.text, 'html.parser')
cells = html.find_all('div', class_='img_and_name')
links = []
for cell in cells:
    for link in cell.find_all('a'):
        if link.text:
            links.append(HOST + link.get('href'))

unis = []

for link in links:
    try:
        while True:
            try:
                page = requests.get(link)
                break
            except Exception as ex:
                print(f'error - {link} - {ex}')

        html = BS(page.text, 'html.parser')
        title = html.find('h4', string='Краткое название')
        uni_name = title.find_next_sibling('p').text
        unis.append(re.split(r', | или |; ', uni_name))
        print(uni_name)
    except Exception as ex:
        print(f'CRITICAL - {link} - {ex}')
        continue



with open(f'../{FOLDER}/raex.json', 'w', encoding='utf-8') as f:
    json.dump(unis, f, ensure_ascii=False, indent=4)