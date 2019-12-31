#!coding=utf-8
from PIL import Image
import os
import math
import threading
from core.build_graph import *

INF = 0xfffffff
M = 30 # 宽度
N = 30 # 高度

# 加载图片
print("[+] Reading files ",end="")
sourceFolder = "./example/puzzle1/shuffle"
files = [ sourceFolder + '/' + file for file in os.listdir(sourceFolder)]
im_list = [Image.open(i) for i in files]
file_count = len(files)
print("Done!")

bestRight = [[INF,0] for i in range(file_count) ] # 最优右图
bestBottom = [[INF,0] for i in range(file_count) ] # 最优下图
Graph = [
    [ 
        [INF,INF] for j in range(file_count) 
    ] for i in range(file_count)
] # 整个比较结果构成的图

print("[+] Begin to compare")
for i in range(len(im_list)):
    r = [INF,0]
    b = [INF,0]
    for j in range(len(im_list)):
        temp = compare(im_list[i],im_list[j])
        Graph[i][j] = temp
        if r[0] > temp[0]:
            r[0] = temp[0]
            r[1] = j
        if b[0] > temp[1]:
            b[0] = temp[1]
            b[1] = j

    bestRight[i] = r
    bestBottom[i] = b
    print("[*] {} best right match:{}".format(files[i],files[r[1]]))
    print("[*] {} best bottom match:{}".format(files[i],files[b[1]]))
    print("[+] Process {}/{}: ".format(i,file_count), end="\r", flush=True)

print("[+] Begin to build image",end="\r\n")

print("[+] Building image of {}x{}".format(M,N))

print("[+] Creating canvas")
width, height = im_list[0].size

print("[+] Begin to build")

for start in range(file_count):
    result = Image.new(im_list[0].mode, (width*M, height*N))
    bestResult = [result,0]
    begin = start
    x = [0 for i in range(file_count)]
    count = 0
    for i in range(N):
        if(x[begin] == 0):
            count+=1
            x[begin] = 1
        result.paste(im_list[begin],box=(0,i*height))
        temp = bestRight[begin][1]
        for j in range(M):
            if(x[temp] == 0):
                count+=1
                x[temp] = 1
            result.paste(im_list[temp],box=(width*(j+1),i*height))
            temp = bestRight[temp][1]
            print("[*] Build {} row / {} col with start:{}".format(i,j,files[start]),end="\r")
        begin = bestBottom[begin][1]
    if(count > bestResult[1]):
        bestResult[0] = result
        bestResult[1] = count
print("[*] Building Done."+" "*10,end='\r\n')
print("[+] Show result")
bestResult[0].show()