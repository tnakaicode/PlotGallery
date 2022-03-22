def average(*args): 
    total = 0
    for a in args:
        total += a
    print(total / len(args))

average(70, 85, 100, 90)
