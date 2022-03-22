class StudentCard:
    def __init__(self, id, name):
        self.__id = id
        self.__name = name

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

a = StudentCard(12345, '鈴木太郎')
#print(a.__id)
#print(a.__name)

print(a.get_id())
print(a.get_name())

