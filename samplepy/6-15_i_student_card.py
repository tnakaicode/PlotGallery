from student_card import StudentCard

class IStudentCard(StudentCard):
    def __init__(self, id, name, nationality):
        self.nationality = nationality
        super().__init__(id, name)
        
    def print_info(self):
        print(f'国籍: {self.nationality}')
        print(f'学籍番号: {self.id}')
        print(f'氏名: {self.name}')
