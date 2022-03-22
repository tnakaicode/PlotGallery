class StudentCard:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def print_info(self):
        print('学籍番号:', self.id)
        print('氏名:', self.name)
