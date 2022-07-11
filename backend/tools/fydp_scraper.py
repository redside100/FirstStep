import json

from bs4 import BeautifulSoup
import requests


# For 2021 pages
def get_page_url(num):
    base = 'https://www.eng.uwaterloo.ca/2021-capstone-design/electrical-computer/participants'
    if 0 <= num <= 10:
        if num == 0:
            return base
        else:
            return base + f'-{num + 1}'


def scrape():
    entries = []
    # 2020
    res = requests.get('https://uwaterloo.ca/capstone-design/2020-electrical-computer-engineering-capstone-design').text
    parser = BeautifulSoup(res, 'html.parser')
    expandables = parser.find_all("div", {
        "class": "expandable"
    })
    for i, expandable in enumerate(expandables):
        entries.append({
            'id': 1000 + i,
            'title': expandable.h2.text.strip(),
            'description': expandable.div.p.text.split("Team members:")[0].strip(),
            'year': 2020
        })

    for i in range(11):
        url = get_page_url(i)
        res = requests.get(url).text
        parser = BeautifulSoup(res, 'html.parser')
        titles = [x.span.text for x in parser.find_all("h2", {
            "class": "im-title"
        })[1:]]
        paragraphs = [x.span.text for x in parser.find_all("p", {
            "class": "im-paragraph"
        })]

        stack = []
        for title in titles:
            if title.isnumeric():
                entries.append({
                    'id': 2000 + int(title),
                    'title': " ".join(stack).strip(),
                    'description': paragraphs.pop(0).strip(),
                    'year': 2021
                })
                stack.clear()
                continue

            stack.append(title)

    with open("2020_2021_ECE_fydp_projects.json", "w+") as f:
        f.write(json.dumps(entries, indent=4))


if __name__ == '__main__':
    scrape()
