from PIL import Image
import math
import threading
from core.logger import logger
import core.vars as vars
import queue

def HSVDistance(hsv_1,hsv_2):   # Calculate color distance
    H_1,S_1,V_1 = hsv_1
    H_2,_,V_2 = hsv_2
    R=100
    angle=30
    h = R * math.cos(angle / 180 * math.pi)
    r = R * math.sin(angle / 180 * math.pi)
    x1 = r * V_1 * S_1 * math.cos(H_1 / 180 * math.pi)
    y1 = r * V_1 * S_1 * math.sin(H_1 / 180 * math.pi)
    z1 = h * (1 - V_1)
    x2 = r * V_2 * S_1 * math.cos(H_2 / 180 * math.pi)
    y2 = r * V_2 * S_1 * math.sin(H_2 / 180 * math.pi)
    z2 = h * (1 - V_2)
    dx = x1 - x2
    dy = y1 - y2
    dz = z1 - z2
    return math.sqrt(dx * dx + dy * dy + dz * dz)

def compare(img1,img2):
    left, right, top, bottom = [],[],[],[]
    imgs = [img1,img2] # Convert to HSV mode
    for im in imgs:
        width = im.size[0]  
        height = im.size[1]
        l,r,t,b = [],[],[],[]
        for i in range(0,height):
            l.append(im.getpixel((0,i))) 
            r.append(im.getpixel((width-1,i)))    
        for i in range(0,width):
            t.append(im.getpixel((i,0))) 
            b.append(im.getpixel((i,height-1)))  
        left.append(l)
        right.append(r)
        top.append(t)
        bottom.append(b)
    result = []
    weight = 0
    for i in range(min(len(right[0]),len(left[1]))): #  img1|img2 
        weight += HSVDistance(right[0][i],left[1][i])
    weight /= min(len(right[0]),len(left[1]))+0.0
    result.append(weight)
    weight = 0
    for i in range(min(len(top[0]),len(bottom[1]))): #    img1/img2
        weight += HSVDistance(top[0][i],bottom[1][i])
    weight /= min(len(top[0]),len(bottom[1]))+0.0
    result.append(weight)
    return result

class CompareWorker(threading.Thread):
    def __init__(self, queue, *args, **kwargs):
        self.queue = queue
        threading.Thread.__init__(self)
    def run(self):
        file_count = vars.get("file_count")
        im_list = vars.get("im_list_hsv")
        files = vars.get("files")
        while True:
            try:
                work = self.queue.get(timeout=3)  # 3s timeout
            except queue.Empty:
                return
            i = work[0]
            j = work[1]
            res = compare(im_list[i],im_list[j])
            GR = vars.get("GR")
            GB = vars.get("GB")
            GR[i][j] = res[0]
            GB[i][j] = res[1]
            vars.set("GR",GR)
            vars.set("GB",GB)
            process_cur = vars.get("process_cur")
            vars.set("process_cur",process_cur+1)
            logger.status("complete: %.2f%% ,working on %s & %s \r" % (100*process_cur/(file_count**2+0.0),files[i],files[j]))
            self.queue.task_done()