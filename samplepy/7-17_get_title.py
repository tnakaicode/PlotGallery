from bs4 import BeautifulSoup

with open('data/ranking.html', 'r', encoding='UTF-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

print(soup.title)

