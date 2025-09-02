'''text = "hello world"
sub = "world"

if sub in text:
    print("Substring found at index:", text.index(sub))
else:
    print("Not found")
'''

def find_str(*args):
    if args[1]=='':
        return 0
    if len(args)==2:
        j=0
        for i in range(len(args[0])):
            if j<len(args[1]):
                if args[0][1]==args[1][j]:
                    j+=1
                    if j==len(args[1]):
                        return i-j+1
                    return -1
                