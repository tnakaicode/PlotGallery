class SimpleCalc:
    @classmethod
    def get_triangle_area(cls, base, height): 
        return base * height / 2

print(SimpleCalc.get_triangle_area(10, 5))