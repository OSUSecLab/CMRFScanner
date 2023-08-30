import queue
import re
import requests
import os
import subprocess
import time
import json
from multiprocessing.managers import BaseManager

def main():
    print("Mini Apps Analyzer")
    print("Warning: this version wipes out mini-apps after analysis")
    task_queue = queue.Queue()
    result_queue = queue.Queue()
    class QueueManager(BaseManager):
        pass
    QueueManager.register('get_task_queue', callable=lambda: task_queue)
    QueueManager.register('get_result_queue', callable=lambda: result_queue)
    manager = QueueManager(address=('', 5000), authkey=b'abc')
    manager.start()
    task = manager.get_task_queue()
    result = manager.get_result_queue()

    analyzed=open('analyzed.csv','r')
    funchecked=open("unchecked.csv",'r')
    analyzedappids=set()
    for line in analyzed.readlines():
        analyzedappids.add(line[:-1])
    analyzed=open('analyzed.csv','a')
    fe=open('error.csv','a')
    outputfolder='output/'
    folderpostfix='42'
    wxapkgfiles=[]
    
    resfile=open('result-priv.csv','a')

    idbatch={}
    with open('unchecked.csv') as f:
        for line in f:
            data=line[:-1].split(',')
            idbatch[data[0]]=data[1]
            # wxapkgfiles.append((data[0],data[1])) # id, batch
    # with open('secondround.txt') as f:
    #     for line in f:
    #         wxid=line[:-1]
    #         wxapkgfiles.append((wxid,idbatch[wxid]))
    with open('cmrfvuln_t.csv') as f:
        for line in f:
            wxid=line.split(',')[0]
            wxapkgfiles.append((wxid,idbatch[wxid]))
    total=len(wxapkgfiles)
    count=0
    print('starting... total amount is '+str(total))
    start=time.time()

    trialcnt=0
    for item in wxapkgfiles:
        
        wxid=item[0]
        batch=item[1]
        if wxid in analyzedappids:
            print('skipped '+str(wxid))
            count+=1
            continue
        trialcnt+=1
        task.put(("/home/allen/Minilab/wxapkgs-"+batch+"w/",batch,wxid,"/home/allen/Github/SP23/DoubleX/src/output/"))
        

    while(count<total):
#                    res={'secrets':set(),'phone':False,'werun':False,'share':False,'group':False,'address':False}
        data = result.get(timeout=1000)
        wxid=data[0]
        batch=data[1]
        res=data[2]
        count+=1;
        print("TIME: {} {}/{}: {}".format(time.time(),count,total,wxid))
        if(len(res)==0):
            # errorapp.write(wxid)
            continue
        if(type(res)==str):
            fe.write(res+"\n")
        else:
            try:
                resfile.write(wxid+";;;"+str(res)+"\n")
                analyzed.write(wxid+'\n')  

            except Exception as e:
                print(e)



    manager.shutdown()
    print('process finished after ' + format(time.time()-start,'.4f') + ' s.')

main()
