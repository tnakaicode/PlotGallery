def print_price(price, func):
    print('価格は' + func(price))

def price_without_tax(price):
    return f'税抜き{price}円'

def price_with_tax(price):   
    return f'税込み{int(price*1.1)}円'

print_price(800, price_without_tax)
print_price(800, price_with_tax)
