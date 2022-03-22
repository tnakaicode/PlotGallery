with open('data/visitor_record.txt', 'r', encoding='UTF-8') as f:
    for line in f:
        if '東京都' in line:
            print(line.replace('\n',''))

