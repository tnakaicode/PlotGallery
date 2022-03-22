import requests

html = requests.get('https://www.shoeisha.co.jp/book/ranking')
print(html.text)
