# 長方形を表すクラス
class Rectangle:
    def __init__(self, width, height):
        self.width = width     # 幅
        self.height = height   # 高さ
        
    # ここに設問のメソッドを追加する
    # [空欄]

            
rec0 = Rectangle(5, 8)
rec1 = Rectangle(4, 6)

print('rec0の面積', rec0.get_area())
print('rec1の面積', rec1.get_area())

if rec0.is_larger(rec1):
    print('rec0 の方が大きい')
else:
    print('rec1 の方が大きい、または同じ')

    
