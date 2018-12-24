import csv
import os

beta=0.4 #判断快恢复的比例
alpha=4  #判断是否距零较近的阈值
dst=0.77 #判断开始下降的比例（为了消除上升过程中抖动的影响）
mini=0.2 #根据下降比例判断是否是慢开始
bbrratio=0.15 #判断BBR是否占主要
symratio=0.2 #判断CUBIC是判断是否对称

paths=[]
out_file='result.txt'
for root,dirs,files in os.walk('.'):
    for file in files:
        paths.append(os.path.join(root,file))
for path in paths: #找文件
    increase=[]
    decrease_steady=[]
    if ".txt" in path and "_draw" not in path:
        with open(path) as f: #读点
            numbers=[]
            while True:
                line=f.readline()
                if not line:
                    break
                number=line.split()
                numbers.append(eval(number[0]))
        if len(numbers)>200: #取前200判断
            numbers=numbers[:199]
        flag=0
        decrease_steady=[]
        decrease_steady.append(numbers[0])
        current=numbers[0]
        number=0   #下降区间个数
        bbrcount=0 #BBR的个数
        recount=0  #Reno的个数
        tacount=0  #Tahoe的个数
        target=path.replace('.txt','_decrease.txt')
        for i in range(1,len(numbers)):
            if (numbers[i]<current) and (numbers[i]>=current*dst) and (flag==0):
                bbrcount=bbrcount+1
            if (numbers[i]<current*dst) and (flag==0): #找到下降起始
                flag=1
                decrease_steady.append(numbers[i])
                current=numbers[i]
                continue
            elif (flag==0) and (numbers[i]>current*dst):#否则放掉该点
                decrease_steady=[]
                decrease_steady.append(numbers[i])
                current=numbers[i]
            elif (flag==1) and (numbers[i]>=current): #下降过程遇到增加，下降结束
                number=number+1 #下降区间加一
                if (current<=decrease_steady[0]*mini) or (current<=alpha): #足够小，是Tahoe的情况
                    tacount=tacount+1
                elif current>=decrease_steady[0]*beta:  #不够小，是Reno的情况
                    recount=recount+1
                decrease_steady=[] #下降区间更新
                decrease_steady.append(numbers[i])
                current=numbers[i]
                flag=0
            elif (flag==1) and (numbers[i]<current): #持续下降，加入点
                decrease_steady.append(numbers[i])
                current=numbers[i]
        if recount>0:
            if recount/bbrcount<bbrratio:
                with open(out_file,'a') as f:
                    strr=""
                    strr=strr+path+": "+"BBR\n"
                    f.write(strr)
            else:   #根据上升区间判断是Reno还是CUBIC
                cubic = 0
                increase = []
                increase.append(numbers[0])
                current = numbers[0]
                for i in range(1, len(numbers)):
                    if numbers[i] >= current:
                        increase.append(numbers[i])
                        current = numbers[i]
                    else:
                        if len(increase) >= 4:
                            cha = []
                            tmp = []
                            for i in range(1, len(increase)):
                                cha.append(increase[i] - increase[i - 1])
                                tmp.append(increase[i] - increase[i - 1])
                            tmp.sort()
                            pos = cha.index(tmp[0])
                            label = 0
                            if (pos > 0) and (pos != len(cha) - 1):#判断上升趋势先减后增
                                for x in range(pos):
                                    if cha[x] < cha[x + 1]:
                                        label = 1
                                for x in range(pos + 1, len(cha)):
                                    if cha[x] < cha[x - 1]:
                                        label = 1
                                t = 1
                                while (pos - t >= 0) and (pos + t < len(cha)):  #判断近似对称
                                    if (abs(cha[pos - t] - cha[pos + t]) > cha[pos-t]*symratio) or \
                                            (abs(cha[pos - t] - cha[pos + t]) > cha[pos+t]*symratio):
                                        label = 1
                                    t = t + 1
                            else:
                                label = 1
                            if label == 0:
                                print(increase)
                                cubic = 1
                        increase = []
                        increase.append(numbers[i])
                        current = numbers[i]
                if cubic == 1:
                    with open(out_file, 'a') as f:
                        strr = ""
                        strr = strr + path + ": " + "CUBIC\n"
                        f.write(strr)
                else:
                    with open(out_file, 'a') as f:
                        strr = ""
                        strr = strr + path + ": " + "Reno\n"
                        f.write(strr)
        if (tacount==number):
            with open(out_file,'a') as f:
                strr=""
                strr=strr+path+": "+"Tahoe\n"
                f.write(strr)
