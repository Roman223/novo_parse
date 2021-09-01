import bs4
import requests
import unicodedata
import re
from inits import *

"""
- Нужно выбрать 10 многоэтажных домов и выгрузить из них данные о продажах квартир. А именно:
•  Адрес объявления (+)
•  Общая площадь квартиры (+)
•  Этаж (+)
•  Год сдачи дома (+)
•  Цена (+)
•  Материал дома (+)
•  Широта и долгота здания в котором размещено объявление (+)
-  Автоматизировать выгрузку (например, раз в день) (+)
Получим 10 домов и все объявления о продажах в них. Получив данные за два дня по одним и тем же домам нужно посчитать изменение средней цены кв.м. в доме.
Поднять БД на PostgreSQL(или любой другой) и загрузить туда выгруженные данные за два дня.
Итогом выполнения ТЗ будет отправленная нам структура БД и примеры любых выполненных запросов на Ваше усмотрение.
"""


def myfilter(name, value):
    if name == "Общая площадь":
        return float(value.replace(" м2", "").replace(',', '.'))
    elif name == 'Этаж':
        # k из n
        return int(value.split('из')[0])
    elif name == 'price':
        return float(re.sub("[^0-9]", "", value))
    elif name == 'm2price':
        return float(value.replace(" ₽/м2", "").replace(' ', ''))
    else:
        return value


def fullness(dict):
    for data in dict.values():
        if len(data.keys()) != 8:
            for k in ['Общая площадь', 'Этаж', 'Материал дома',
                      'location', 'geo', 'build_date', 'price', 'm2price']:
                if k not in data.keys():
                    if k == 'geo':
                        data[k] = (0, 0)
                    else:
                        data[k] = 0

    return dict


def parseit(urls):
    output = {}

    n = 1

    loc = None
    for url in urls:
        # print(url)
        print(f"{n}/{len(urls)}")
        unit = {}

        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.content, 'html.parser')

        # Баг, если использовать все в одном цикле. Выдает только общую площадь

        for address, hn in zip(
                soup.find_all('span', class_='address'),
                soup.find_all('span', class_='house-number')
        ):
            # {hn.text.strip(', ')}
            loc = f"""{re.sub('[^0-9|/]', "", hn.text.strip(', ')).split("/")[0]} {address.text.strip(', ')} Новосибирск"""
            unit['location'] = loc

            location_ = geolocator.geocode(loc)
            print(loc)
            if location_:
                unit['geo'] = (location_.latitude, location_.longitude)
            else:
                unit['geo'] = (0, 0)

        for descriptor, value in zip(soup.find_all('div', class_='caption'),
                                     soup.find_all('div', class_='text')):
            if descriptor.text == 'год сдачи':
                unit['build_date'] = int(value.text)
                break
            else:
                continue

        for name, value in zip(
                soup.find_all('span', class_='card-living-content-params-list__name'),
                soup.find_all('span', class_='card-living-content-params-list__value')
        ):
            if name.text in NAMES:
                unit[name.text] = myfilter(name.text, unicodedata.normalize(u'NFKD', value.text))

        for price in soup.find_all('span', class_='price'):
            unit['price'] = myfilter('price', unicodedata.normalize(u'NFKD', price.text))

        for m2price in soup.find_all('div', class_='part-price'):
            unit['m2price'] = myfilter('m2price', unicodedata.normalize(u'NFKD', m2price.text))

        output[n] = unit
        n += 1

    return output


with open('links.txt') as f:
    links_houses = [line.strip() for line in f.readlines()]
    f.close()

links = []
for link in links_houses:
    instances_soop = bs4.BeautifulSoup(requests.get(link).content, 'html.parser')
    hl = ["https://novosibirsk.n1.ru" + i['href'] for i in instances_soop.find_all('a', href=True) if
          'view' in i['href']]
    for flat in hl:
        links.append(flat)

package = parseit(links)

package = fullness(package)

# with open('data.json', 'w+', encoding='utf-8') as f:
#     json.dump(package, f, ensure_ascii=False, indent=4)

# for name, value in package.items():
#     print(f"{name} : {value}")

mycursor.execute("USE novo_parse;")

for data in package.values():
    mycursor.execute(
        f"""
            INSERT INTO novo_parse.main_data (location, size, parsing_date, fabric, floor, build_date, latitude, longitude, price, m2price)
            values ('{data['location']}', {data['Общая площадь']}, '{now.strftime("%m/%d/%Y, %H:%M:%S")}',
            '{data['Материал дома']}', {data['Этаж']}, {data['build_date']}, {data['geo'][0]},{data['geo'][1]}, {data['price']}, {data['m2price']});
            """
    )
    mydb.commit()
