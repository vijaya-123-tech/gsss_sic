#chocolate problem 

num=int(input("enter the total number of chocolate"))
list=[]
for i in range(num):
    list1=int(input())
    list.append(list1)
ref = list[0]
list1=[]
list2=[]
for i in range(num):
    if ref < list[i]:
        list1.append(list[i])
    else:
        list2.append(list[i])
print(list1)
print(list2)