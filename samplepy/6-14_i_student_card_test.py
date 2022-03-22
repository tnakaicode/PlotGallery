from i_student_card import IStudentCard

a = IStudentCard(2345, 'John Smith', 'イギリス')

print(f'a.id:{a.id}')
print(f'a.name:{a.name}')
print(f'a.nationality:{a.nationality}')
a.print_info()
