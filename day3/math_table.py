#to run - cmd --> math_table.py 15

import sys
print (sys.argv)#list
print(type(sys.argv))# tells type like (it is list)
print(sys.argv[0])
number=int(sys.argv[1])
print(f'user given number is {number}') 

for i in range(1,21):
    print('%d *%02d =%03d' %(number,i,number*i))