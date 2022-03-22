print('a ÷ b の計算をします')
try:
    a = input('aの値を入力してください: ')
    b = input('bの値を入力してください: ')
    c = float(a) / float(b)
    print('答えは', c)
except ValueError:
    print('入力が数字ではありません')
except ZeroDivisionError:
    print('ゼロで割ることはできません')

print('処理を終わります')
