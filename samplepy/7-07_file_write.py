f = open('output.txt', 'w', encoding='UTF-8') 
for i in range(0,100):
    f.write(str(i) + '\n') 
f.close()
