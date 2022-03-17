#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os  
import time
from functools import wraps
   
   

def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        r = func(*args, **kwargs)
        end = time.perf_counter()
        print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
        return r
    return wrapper
    
    
def finddir(path):
    for root, dirs, dirs in os.walk(path):
        for i in range(0,len(dirs)): 
            dir = os.path.join(root, dirs[i])
            list1.append(dir)
    return list1
    
    
def findtxt(path):
    for root, dirs, files in os.walk(path):
        for i in range(0, len(files)):
            file = files[i]
            (name, ext) = os.path.splitext(file)
            if ext == ".TXT" or ext == ".txt":
                path = os.path.join(root, file)
                list2.append(path)
    return list2
    
    
def savefile(path, text):
    if not os.path.exists(path):
        with open(path, "w", encoding = "UTF-8") as f:
            f.write(text)
            f.close()
        
        
def removefile(list):
    for i in range(0, len(list)):
        dir = str(list[i])
        path = os.path.join(dir,".txt")
        path = path.replace("\.", ".")
        if os.path.exists(path):
            os.remove(path)
            
            
def combine(list1, list2):
    for i in range(0, len(list1)):
        dir = str(list1[i])
        text = ""
        for j in range(0, len(list2)):
            path = str(list2[j])
            if dir in path and os.path.exists(path):
                try:
                    with open(path,"r", encoding = "UTF8") as f:
                        text += f.read() + "\n"
                except UnicodeError:
                    with open(path,"r", encoding = "GBK") as f:
                        text += f.read() + "\n"
                        
                (tempath, name) = os.path.split(path)
                print(name)
        
        path = os.path.join(dir,".txt")
        path = path.replace("\.", ".")
        (tempath, name) = os.path.split(path)
        
        savefile(path, text)
        print("上述文件合并为【" + name + "】")
        print("————————————————")
        
        
@timethis
def main(): 
    print("TXT合并开始：")
    print("————————————————")
    removefile(list1)
    combine(list1, list2)
    print("全部文件合并完成")

    
if __name__ == '__main__':
    list1 = []; list2 = []; 
    path = os.getcwd()
    list1 = finddir(path)
    list2 = findtxt(path)
    
    if list1 != [] and list2 != []:
        main()
        os.system("pause")
        
    else:
        print("请把本文件放在单章小说的上级文件夹中")
        print("请把本文件放在单章小说的上级文件夹中")
        print("当前目录：")
        print(path)
        os.system("pause")
        
        
