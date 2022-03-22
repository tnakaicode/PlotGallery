f = open('data/visitor_record.txt', 'r', encoding='UTF-8') 
lines = f.readlines()

for line in lines:
    if '東京都' in line:
        print(line.replace('\n',''))

f.close()
