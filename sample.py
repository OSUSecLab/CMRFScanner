#!/usr/bin/python3
import subprocess
import os
ids={}
with open('unchecked.csv','r') as f:
    for line in f:
        if line.split(',')[1][:-1]=='':
            continue
        ids[line.split(',')[0]]=line.split(',')[1][:-1]

with open('unused.csv','r') as f:
    for line in f:
        if line.split(',')[1][:-1]=='':
            continue
        ids[line.split(',')[0]]=line.split(',')[1][:-1]

id=0
with open('random_fp.csv','r') as f:
    for line in f:
        id+=1
        print(line)
        # exit()
        for i in range(0,20):
            print(id)
        wxid=line.split("\n")[0].split(',')[0]
        print(ids[wxid],wxid)
        os.system('./unpack_and_decrypt.sh '+str(ids[wxid])+" "+str(wxid))
        # exit()