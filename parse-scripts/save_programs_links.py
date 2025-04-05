from parsing.parse_functions import get_programs
from parsing.config import FOLDER
import pickle


FILENAME = 'programs-links.pkl'

with open(f'{FOLDER}/universities-info.pkl', 'rb') as file:
    uni_links = pickle.load(file)

with open(f'{FOLDER}/{FILENAME}', 'rb') as file:
    data = pickle.load(file)


for i, uni_info in enumerate(uni_links, start=1):
    if data.get(uni_info):
        continue

    print(f'\n{i}. {uni_info[0]}')
    data[uni_info] = get_programs(uni_info[1], 'bakispec'), get_programs(uni_info[1], 'magistratura')

    with open(f'{FOLDER}/{FILENAME}', 'wb') as file:
        pickle.dump(data, file)
