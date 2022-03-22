def countdown(start, end):
    print('1つ目の引数で受け取った値:', start)
    print('2つ目の引数で受け取った値:', end)
    print('カウントダウンをします')
    counter = start
    while counter >= end:
        print(counter)
        counter -= 1

countdown(7, 3)
