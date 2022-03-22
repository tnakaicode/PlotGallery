from bs4 import BeautifulSoup

with open('data_ranking.html.txt', 'r', encoding='UTF-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser') 

for sec in soup.select('section'):
    if(sec.select_one('h2')):
        category = sec.select_one('h2').text
        url = sec.select_one('ul').select_one('li').select_one('a').get('href')
        
        print('カテゴリ：', category)
        print('書籍のURL:', url)
