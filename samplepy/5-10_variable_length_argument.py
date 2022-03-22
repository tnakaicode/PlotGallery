def print_data(**kwargs):
    for key, value in kwargs.items(): 
        print(f'キー:{key}, 値:{value}')

print_data(item='リンゴ', count=1, price=120)
