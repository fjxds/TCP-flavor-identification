import csv
import os

paths=[]
for root,dirs,files in os.walk('.'):
    for file in files:
        paths.append(os.path.join(root,file))
for path in paths:
    if (".txt" in path) and ("_draw" not in path) and ("result" not in path):
        with open(path) as f:
            numbers=[]
            while True:
                line=f.readline()
                if not line:
                    break
                number=line.split()
                numbers.append(eval(number[0]))
        out_file=path.replace('.txt','_draw.txt')
        if (len(numbers)>200):
            numbers=numbers[:199]
        with open(out_file,'w') as f:
            strr="["
            for number in numbers:
                strr=strr+str(number)
                strr=strr+","
            strr+="]"
            f.write(strr)


