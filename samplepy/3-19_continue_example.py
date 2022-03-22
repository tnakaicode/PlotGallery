total = 0
for i in range(100):
    if i % 3 == 0:
        continue
    print(i)
    total += i

print('合計は', total)
