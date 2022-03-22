def is_positive(i):
    if i > 0:
        return True
    else:
        return False

a = -10;
if is_positive(a) == True:
    print('aの値は正です')
else:
    print('aの値は負またはゼロです')
