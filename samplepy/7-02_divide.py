print('a ÷ b の計算をします')
try:
    a = input('aの値を入力してください: ')
    b = input('bの値を入力してください: ')
    c = float(a) / float(b)
    print('答えは', c)
except:
    print('入力が適切ではありません')

print('処理を終わります')
