import sys

print('User given input is \n', sys.argv[1:])

states = []
capitals = list()

for string in sys.argv[1:]:
    temp_list = string.split(' ')
    states.append(temp_list[0])
    capitals.append(temp_list[1])

print('-' * 24)
print('%-15s %s'%('STATE', 'CAPITAL'))
print('-' * 24)
for i in range(len(states)):
    print('%-15s %s'%(states[i], capitals[i]))
