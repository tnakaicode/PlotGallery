# 個人の情報を表すクラス
class Person:
    def __init__(self, name, age):
        self.name = name  # 名前
        self.age = age   # 年齢

# ここに設問の関数を追加する

#(1)
def print_info(p):
    print('名前', p.name)
    print('年齢', p.age)

#(2)
def age_check(p, i):
    return p.age > i
    
#(3)
def print_younger_person_name(p1, p2):
    if p1.age <= p2.age:
        print(p1.name)
    else:
        print(p2.name)
        
#(4)
def get_total_age(p1, p2):
    return p1.age + p2.age

a = Person("高橋太郎", 19)
b = Person("小林花子", 18)

# 追加した関数を呼び出す。戻り値がある場合は出力する
#(1)
print_info(a)

#(2)
print(age_check(a, 20))

#(3)
print_younger_person_name(a, b)

#(4)
print(get_total_age(a, b))

