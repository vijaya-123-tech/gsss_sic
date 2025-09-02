import sys

input_argument=sys.argv[1:]
print("user entered input is",input_argument)

list=[]
states=[]
capital=[]
for i in range(len(input_argument)):
    my_input=input_argument[i].split()
    list.append(my_input)
    states.append(list[i][0])
    capital.append(list[i][1])

print('%-15s %-10s' %("states", "capital" ))
print('-'*25)
for i in range(len(states)):
    print('%-15s %-10s' %(states[i] ,capital[i] ))