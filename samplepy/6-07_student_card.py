class StudentCard:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def print_info(self):
        print('学籍番号:', self.id)
        print('氏名:', self.name)

a = StudentCard(1234, '鈴木太郎')
b = StudentCard(1235, '佐藤花子')
a.print_info()
b.print_info()
