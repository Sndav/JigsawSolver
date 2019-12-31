#!coding=utf-8
from PIL import Image
import os
import threading
from core.build_graph import *
import core.vars as vars
from core.logger import logger
import queue

INF = 0xfffffff
M = 30 # 宽度
N = 30 # 高度
thread_num = 50

vars._init()
# 加载图片
logger.info("Reading files")
sourceFolder = "./example/puzzle2"
files = [ sourceFolder + '/' + file for file in os.listdir(sourceFolder)]
im_list = [Image.open(i) for i in files]
file_count = len(files)
im_list_hsv = [0 for i in range(file_count)]
logger.success("Done!")

GraphR = [
    [ 
        INF for j in range(file_count) 
    ] for i in range(file_count)
] # 右图
GraphB = [
    [ 
        INF for j in range(file_count) 
    ] for i in range(file_count)
] # 整个比较结果构成的图
vars.set("file_count",file_count)
vars.set("process_cur",0)
vars.set("GR",GraphR)
vars.set("GB",GraphB)
vars.set("files",files)
vars.set("im_list_hsv",im_list_hsv)

logger.info("Begin to compare")
workQueue = queue.Queue()
for i in range(file_count):
    im_list_hsv[i] = im_list[i].convert('HSV')
    for j in range(file_count):
        workQueue.put([i,j])  

for _ in range(thread_num):
    CompareWorker(workQueue).start()
workQueue.join()  # blocks until the queue is empty.

Graph = vars.get("G")

logger.info("Begin to build image")

logger.info("Building image of {}x{}".format(M,N))

logger.info("Creating canvas")
width, height = im_list[0].size

logger.info("Begin to build")


result = Image.new(im_list[0].mode, (width*M, height*N))
begin = 0
x = [0 for i in range(file_count)]
GR = vars.get("GR")
GB = vars.get("GB")

def minn(arr,x):
    res = INF
    p = 0
    for i in range(len(arr)):
        if arr[i] < res and x[i] == 0:
            res = arr[i]
            p = i
    return p
for i in range(N):
    if(min(x) == 1):
        x = [0 for i in range(file_count)]
    begin = minn(GB[begin],x)
    temp = begin
    for j in range(M):
        result.paste(im_list[temp],box=(width*(j+1),i*height)) 
        temp = minn(GR[temp],x)
        x[temp] = 1
        logger.status("Build {} row / {} col".format(i,j))

logger.success("Building Done")
logger.success("Show result")
result.show()