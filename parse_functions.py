import requests
from bs4 import BeautifulSoup as BS
from config import HOST, ABOUT


UPPER_BOUND = float('inf')


session = requests.Session()
session.cookies.update({
    'into_vzp_uid': 'eyJpdiI6Ild4RFlBT3BGMGVPb2cvb29YZzNmeFE9PSIsInZhbHVlIjoiMWhxRUIxUzZVdWpta0ZkeTVpYmJoZG9TVW9qVm1CV3UzemZSQldhc1RFcFlQd3NaODRiVWZwMmJvNnQ2MHFldjkwdWNUWm9rRkVlYlpNKzNSOHF3YWNoRUQvYXpoVUkxeHNHbGdUdUhxR1E9IiwibWFjIjoiNTU5ZTVkNDNkYTAwMTc4N2ViODkyN2Q2MmFkYWY1ZTVkYWQ2Mzc1YmYxMzVmZGE0ZDQ3NzA0N2U5MjQ2ZDg3MyIsInRhZyI6IiJ9',
    'october_session': 'eyJpdiI6IlA1TExqdmxVWC95aEY3V1R5YTR5eUE9PSIsInZhbHVlIjoiQ1dJQlJ4QlVMNFA2K0Y3aHpSTDVuV1FZL1hiM01ZeEFnaEV6TkovbU8valQ4eTBWQzRyRll1NlZGeEgwUjRBWDdFT0JOVzFwbTJOZ1dDeEhSWHk0TlJmRjlpMS9Qb2lrQjR0MDhtSU1CV3AyK3VFN2NzK2hJRkZwZzZ1ckJST1MiLCJtYWMiOiJmMDg2NzE2N2U4MzE3OTYyYzZiMTQwZTYyODljZThkNzUxNWFiYmJiMzFmYjUyOWQyMWJhMDg0ZWVkYmU5NzExIiwidGFnIjoiIn0%3D',
    'user_auth': 'eyJpdiI6Imk2ZXdqV3dDN3NoZ2dCOWoxZUlyY2c9PSIsInZhbHVlIjoiNzdxdjhNYTRNSEdqbWFuTS9sdWJiL1RkQm1NMG01Q0hxbS9aRmRLRlFabG9CdEhRSDY3M2JtaUZEWWhWYTJXNU9veGFiLzRrSEpCS2VMenA3ZWE5R05TV3cwTzQxb2tXbG51ellBa2ZUY1lxNEs0dnZteVZKdS9YdWlLUkE0Ny9QdFMrZm5OVis0RzNrVFFGQVBHZHV2ZzMzeERpbW40UG5MM0xqUnh1cURJPSIsIm1hYyI6Ijg4YjkxYjM5MDBhNjAwZWM5Y2EyOTAyMDFmMjM3NWQyNDMwMzMwYmEwODMzYjI3NWYzYzRhMzBlNzgwNGE0YzQiLCJ0YWciOiIifQ%3D%3D'
})


def get_html(url):
    last_ex = None
    for _ in range(5):
        try:
            page = session.get(url)
            break
        except Exception as ex:
            last_ex = ex
    else:
        raise last_ex

    status = page.status_code
    print(f'{url} - {status}')
    if status != 200:
        raise requests.exceptions.HTTPError(f'статус код: {status}')
    return BS(page.text, 'html.parser')


def make_dict(text):
    if not text:
        return None
    arr = text.replace(' или ', '/').split('/')
    exams = {}
    arr[0] = arr[0].replace('На выбор:', '').strip()
    pairs = list(map(lambda x: x.rsplit(' - ', 1), arr))
    last_value = pairs[-1][1]
    for pair in pairs:
        key = pair[0].split('. ')[::-1][0]
        value = int(pair[1] if len(pair) == 2 else last_value)
        exams[key] = value
    return exams


def get_universities():
    i = 1
    uni_pages = []
    while i < UPPER_BOUND:
        link = f'{HOST}/vuz?page={i}'
        html = get_html(link)

        uni_cards = html.find_all('div', class_='vuzesfullnorm')
        if not len(uni_cards):
            break

        for card in uni_cards:
            link = card.find('a')
            uni_id = int(link.get('href').split('/')[-1])
            uni_pages.append((link.find('img').get('alt')[8:], uni_id))

        i += 1

    return uni_pages


def get_programs(uni_id, level):
        edu_pages = []
        i = 1
        while i < UPPER_BOUND:
            link = f'{HOST}/vuz/{uni_id}/programs/{level}?page={i}'
            html = get_html(link)

            edu_cards = html.find_all('div', class_='col-md-12 col-sm-6 blockNewItem')
            if not len(edu_cards):
                break

            for card in edu_cards:
                if card.get('style') == 'opacity:0.4;':
                    break
                card_link = card.find('a', class_='newItemSpPrTitle')
                prog_id = card_link.get('href').split('/')[-1]
                edu_pages.append(int(prog_id))

            i += 1

        return edu_pages


def get_program_info(prog_url):
    info = {'Варианты поступления': {}}

    html = get_html(prog_url)

    # Проверка на актуальную программу
    if html.find('div', id='notPublished'):
        return None, None, None

    # Ищем название ОП и полное наименование вуза
    intro = html.find_all('div', class_='textOPisanieMidAfterTitle')[1].next
    prog_name = intro[intro.find('«')+1 : intro.find('»')]
    uni_name = intro[intro.find('реализует')+len('реализует')+1 : intro.find('с подробнейшей')-1]

    # Инфа из основной таблицы
    main_info = html.find('div', class_='podrInfo').find_all('div', recursive=False)
    for option in main_info[1:]:
        key, val = option.text.split(':')
        val = val.strip()
        if key == 'Форма обучения':
            val = val.split('; ') if val else []
        if key == 'Срок обучения':
            val =  list(map(lambda x: float(x.split()[0]), val.split('; '))) if val else []
        info[key] = val

    # Ищем начало блока с описанием ОП
    about_title = html.find('div', id='chemy')
    if about_title:
        key = ABOUT  # about_title.text.strip()

        # Собираем весь текст блока вместе
        about_text = ''
        while True:
            about_title = about_title.find_next_sibling()
            if about_title.name != 'p':
                courses = map(lambda x: x.text, about_title.find_all('li'))
                about_text += ', '.join(courses)
                break
            else:
                about_text += about_title.text + '\n'

        if about_text:
            info[key] = about_text


    # Добавляем инфу о егэ и вступительных
    content = html.find('div', class_='sideContent progpagege')
    exams = content.find_all('div', class_='newCombBlock')
    for var in exams[:len(exams) // 2]:
        key = var.find('div', class_='labelNewCombBlock').next
        values = var.find_all('div', class_='itemNewBlockComb')
        values = map(lambda x: make_dict(x.text), values)
        info[key.strip()] = [x for x in list(values) if x is not None]

    #=======================================================================================================#

    html = get_html(prog_url + '/varianty')

    variants = html.find_all('div', class_='newInfooItem')
    for variant in variants:
        data = variant.find_all('div', recursive=False)
        config = data[1].text
        info['Варианты поступления'][config] = {}

        for i in (2, 3):
            params = data[i].find('div').find_all('div', recursive=False)
            key = params[0].find('span').text
            info['Варианты поступления'][config][key] = {} if len(params) > 1 else 'нет набора на бюджет'

            for p in params[1:]:
                val = p.find('b')
                if val:
                    val = val.text.rstrip(' ₽')
                    val = int(val) if val.isdigit() else float(val)
                info['Варианты поступления'][config][key][p.next.rstrip(': ')] = val

    return uni_name, prog_name, info