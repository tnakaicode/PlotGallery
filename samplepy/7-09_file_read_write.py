with open('output.txt', 'w', encoding='UTF-8') as out_file:
    with open('data/visitor_record.txt', 'r', encoding='UTF-8') as in_file:
        for line in in_file:
            if '東京都' in line:
                out_file.write(line)
