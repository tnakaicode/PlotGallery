class StudentCard:
    def __init__(self, id, name):
        self.id = id
        self.name = name

a = StudentCard(1234, '鈴木太郎')
b = StudentCard(1245, '佐藤花子')

print(f'a.id:{a.id}, a.name:{a.name}')
print(f'b.id:{b.id}, b.name:{b.name}')
