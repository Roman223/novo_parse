import bs4
import requests

URL = "https://novosibirsk.n1.ru/kupit/kvartiry/?limit=100"

houses_links = requests.get(URL)
houses_links = bs4.BeautifulSoup(houses_links.content, 'html.parser')


def clear_address(address):

    elems = address.split(",")

    elems[2] = "".join(elems[2].split('/')[0])
    # print(elems)
    return ",".join(elems[1:])


links_1 = {location: link for location, link in
           zip([clear_address(a.text) for a in
                houses_links.find_all('span', class_='link-text')],
               ["https://novosibirsk.n1.ru" + a['href'] for a in houses_links.find_all('a', href=True) if
                'view' in a['href']])}

print(links_1)
links_2 = []
n = 0
for link in links_1.values():
    if n == 10:
        break
    room_soup = bs4.BeautifulSoup(requests.get(link).content, 'html.parser')
    # print(["https://novosibirsk.n1.ru" + i['href'] + '&limit=100' for i in room_soup.find_all('a', href=True) if ('search' and 'addresses') in i['href']])
    try:
        links_2.append(
            *["https://novosibirsk.n1.ru" + i['href'] + '&limit=100' for i in room_soup.find_all('a', href=True) if
              ('search' and 'addresses') in i['href']]
        )
        for name, value in links_1.items():
            if value == link:
                print(name, value)
        n += 1
    except TypeError:
        continue

with open('links.txt', 'a+') as f:
    for link in links_2:
        f.write(link)
        f.write('\n')
