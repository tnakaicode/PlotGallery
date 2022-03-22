class X:
    def __init__(self):
        print('[x]')
    
    def a(self):
        print('[x.a]')

    def b(self):
        print('[x.b]')

class Y(X):
    def __init__(self):
        super().__init__()
        print('[y]')
    
    def a(self):
        print('[y.a]')
        super().a()

x = X()
x.a()
x.b()
y = Y()
y.a()
y.b()
