import requests
from bs4 import BeautifulSoup

result = requests.get('https://www.shoeisha.co.jp/book/ranking')
soup = BeautifulSoup(result.text, 'html.parser')
print(soup.title)
