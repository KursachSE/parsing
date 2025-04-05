import json
import pandas as pd
from parsing.config import BAK, MAG, ABOUT, LINK, FULL_NAME


NAME = 'programs-info'
substrings = ['ЕГЭ', 'Вступительные', 'Военн']


with open(f'{NAME}.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

with open(f'raex.json', 'r', encoding='utf-8') as file:
    raex = json.load(file)

def find_top(uni_name):
    for i in range(100):
        if uni_name in raex[i]:
            return i + 1
    return None


def change_key(v):
    for option in v.values():
        budget = option.get('Бюджет')
        paid = option.get('Платное')
        for var in [budget, paid]:
            if not isinstance(var, dict):
                continue
            for key in list(var.keys()):
                if 'балл' in key:
                    var['Проходной балл'] = var.pop(key)
                elif 'мест' in key:
                    var['Мест'] = var.pop(key)
    return v


rows = []
for uni, uni_info in data.items():
    full_name = uni_info[FULL_NAME]
    for level in (BAK, MAG):
        for prog, prog_info in uni_info[level].items():
            d = {'Программа': prog, 'Университет': uni, 'Место в топе': find_top(uni)}
            for k, v in prog_info.items():
                for sub in substrings:
                    if sub in k:
                        k = 'ВУЦ/ВК' if sub == 'Военн' else sub
                        v = d.get(k) if v is None else v
                if k == ABOUT:
                    v = (v.replace(',\n', ', ').replace('\u00A0', ' ')
                         .replace(': \n', ': ').replace(':\n', ': ').replace(';,', ','))
                if k == 'Варианты поступления':
                    v = change_key(v)
                d[k] = v
            rows.append(d)


df = pd.DataFrame(rows).dropna(subset=[ABOUT])
df.drop(LINK, axis=1, inplace=True)
df = df[df['Квалификация'] != 'Специализированное высшее']
df.to_json(f'{NAME}-lines.json', orient='records', force_ascii=False, indent=4)
