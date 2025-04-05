from parsing.parse_functions import get_program_info
from parsing.config import HOST, BAK, MAG, FULL_NAME, LINK, FOLDER
import json
import pickle
import logging


PATH = f'../{FOLDER}/programs-info.json'
lvl_map = {BAK: 'bakispec', MAG: 'magistratura'}


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)
logging.info('Программа начала выполнение')


with open(f'../{FOLDER}/programs-links.pkl', 'rb') as file:
    prog_dict = pickle.load(file)

with open(PATH, 'r', encoding='utf-8') as file:
    data = json.load(file)


for i, (uni_info, programs) in enumerate(prog_dict.items(), start=1):
    uni_name, uni_id = uni_info

    logging.info(f'{i}. {uni_name}')

    uni_url = f'{HOST}/vuz/{uni_id}'

    if not data.get(uni_name):
        data[uni_name] = {
            FULL_NAME: '',
            LINK: uni_url,
            BAK: {},
            MAG: {}
        }

    for level, progs in [(BAK, programs[0]), (MAG, programs[1])]:
        existing_links = {p[LINK] for p in data.get(uni_name, {}).get(level, {}).values()}

        for prog_id in progs:
            prog_url = f'{uni_url}/programs/{lvl_map[level]}/{prog_id}'
            if prog_url in existing_links:
                continue

            try:
                uni_full_name, prog_name, info = get_program_info(prog_url)
                if info is None:
                    continue

                if data[uni_name][level].get(prog_name):
                    j = 1
                    while data[uni_name][level].get(prog_name + f' (дубликат {j})'):
                        j += 1
                    prog_name = prog_name + f' (дубликат {j})'

                data[uni_name][FULL_NAME] = uni_full_name
                data[uni_name][level][prog_name] = {
                    LINK: prog_url,
                    **info
                }
            except Exception as ex:
                logging.error(prog_url + ' - ' + str(ex))


    with open(PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


logging.info('Программа завершила выполнение')