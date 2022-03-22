# 日付ごとに訪問者を格納するための辞書
day_count_dict = {}

with open('data_visitor_record.txt', 'r', encoding='UTF-8') as f:
    for line in f:
        date, pref, num_adult, num_children = line.split(',')
        num_all = int(num_adult) + int(num_children)
        
        # 日付ごとに訪問者数を加算
        if date in day_count_dict:  # キーがあれば値を変更
            day_count_dict[date] += num_all
        else:                       # キーがなければ要素を作成
            day_count_dict[date] = num_all

# 訪問者数でソート
day_count_sorted = sorted(day_count_dict.items(), key=lambda x:x[1], reverse=True)

# ソート済みの先頭の要素を出力
print(day_count_sorted[0])
