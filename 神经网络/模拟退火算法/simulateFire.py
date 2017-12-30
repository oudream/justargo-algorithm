'''
	模拟退火算法
	
	
'''
import numpy as np
import plot as pt

coordinates = np.array([[565.0,575.0],[25.0,185.0],[345.0,750.0],[945.0,685.0],[845.0,655.0],
                        [880.0,660.0],[25.0,230.0],[525.0,1000.0],[580.0,1175.0],[650.0,1130.0],
                        [1605.0,620.0],[1220.0,580.0],[1465.0,200.0],[1530.0,  5.0],[845.0,680.0],
                        [725.0,370.0],[145.0,665.0],[415.0,635.0],[510.0,875.0],[560.0,365.0],
                        [300.0,465.0],[520.0,585.0],[480.0,415.0],[835.0,625.0],[975.0,580.0],
                        [1215.0,245.0],[1320.0,315.0],[1250.0,400.0],[660.0,180.0],[410.0,250.0],
                        [420.0,555.0],[575.0,665.0],[1150.0,1160.0],[700.0,580.0],[685.0,595.0],
                        [685.0,610.0],[770.0,610.0],[795.0,645.0],[720.0,635.0],[760.0,650.0],
                        [475.0,960.0],[95.0,260.0],[875.0,920.0],[700.0,500.0],[555.0,815.0],
                        [830.0,485.0],[1170.0, 65.0],[830.0,610.0],[605.0,625.0],[595.0,360.0],
                        [1340.0,725.0],[1740.0,245.0]])

def getdistmat(coordinates):
    num = coordinates.shape[0]
    distmat = np.zeros((52,52))
    for i in range(num):
        for j in range(i,num):
            distmat[i][j] = distmat[j][i]=np.linalg.norm(coordinates[i]-coordinates[j])
    return distmat

def initpara():
    alpha = 0.95
    t = (1,100)
    markovlen = 100 #在当前温度下，要循环测试多少次
    repeatFT = 100  #循环100次都没有找到更优的解，则认为没有更优的解了

    return alpha,t,markovlen,repeatFT

def calcdist(distmat,solutionnew,num):
    valuenew = 0
    for i in range(num-1):
        valuenew += distmat[solutionnew[i]][solutionnew[i+1]]
    valuenew += distmat[solutionnew[0]][solutionnew[num-1]]
    return valuenew
	
num = coordinates.shape[0]
distmat = getdistmat(coordinates)



solutionnew = np.arange(num)
valuenew = calcdist(distmat,solutionnew,num)

solutioncurrent = solutionnew.copy()
valuecurrent = valuenew

solutionbest = solutionnew.copy()
valuebest = valuenew

alpha,t2,markovlen,repeatFT = initpara()
t = t2[1]

result = [] #记录迭代过程中的最优解

while t > t2[0]:
    stoc = 0 #代表站在原位的次数
    for i in np.arange(markovlen):	
        #下面的两交换和三角换是两种扰动方式，用于产生新解
        if np.random.rand() > 0.5:# 两交换
            # np.random.rand()产生[0, 1)区间的均匀随机数
            while True:#产生两个不同的随机数
                loc1 = np.int(np.ceil(np.random.rand()*(num-1)))
                loc2 = np.int(np.ceil(np.random.rand()*(num-1)))
                if loc1 != loc2:
                    break
            solutionnew[loc1],solutionnew[loc2] = solutionnew[loc2],solutionnew[loc1]
        else: #三交换
            while True:
                loc1 = np.int(np.ceil(np.random.rand()*(num-1)))
                loc2 = np.int(np.ceil(np.random.rand()*(num-1))) 
                loc3 = np.int(np.ceil(np.random.rand()*(num-1)))

                if((loc1 != loc2)&(loc2 != loc3)&(loc1 != loc3)):
                    break

            # 下面的三个判断语句使得loc1<loc2<loc3
            if loc1 > loc2:
                loc1,loc2 = loc2,loc1
            if loc2 > loc3:
                loc2,loc3 = loc3,loc2
            if loc1 > loc2:
                loc1,loc2 = loc2,loc1

            #下面的三行代码将[loc1,loc2)区间的数据插入到loc3之后
            tmplist = solutionnew[loc1:loc2].copy()
            solutionnew[loc1:loc3-loc2+1+loc1] = solutionnew[loc2:loc3+1].copy()
            solutionnew[loc3-loc2+1+loc1:loc3+1] = tmplist.copy()  

        valuenew = calcdist(distmat,solutionnew,num)

        if valuenew < valuecurrent: #接受该解
            #更新solutioncurrent 和solutionbest
            valuecurrent = valuenew
            solutioncurrent = solutionnew.copy()

            if valuenew < valuebest:
                valuebest = valuenew
                solutionbest = solutionnew.copy()
                stoc = 0
            else:
                stoc += 1 #代表没有找到更优的解
        else:#按一定的概率接受该解
            if np.random.rand() < np.exp(-(valuenew-valuecurrent)/t):
                valuecurrent = valuenew
                solutioncurrent = solutionnew.copy()
            else:
                solutionnew = solutioncurrent.copy() #此处代表变换 村庄的顺序，变了之后，没有计算得到满意的结果，必须再次变回原来的村庄顺序
            stoc += 1	#代表没有做任何改变
        if stoc >= repeatFT:      #代表连续10次都没有找到更好的解
            print('连续%d次都没有找到更好的解:%d' % (repeatFT,i))
            break;
    t = alpha*t
    result.append(valuebest)
    print(t) #程序运行时间较长，打印t来监视程序进展速度

print(solutionbest)	
	
dataArr = np.zeros((len(result),2))
for i in range(len(result)):
	dataArr[i][0] = i
	dataArr[i][1] = result[i]
pt.plotPoint(np.mat(dataArr))
#plot(np.array(result))
#ylabel("bestvalue")
#xlabel("t")