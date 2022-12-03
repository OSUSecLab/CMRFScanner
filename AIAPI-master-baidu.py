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

    analyzed=open('analyzed_b.csv','r')
    funchecked=open("baiduids.csv",'r')
    analyzedappids=set()
    for line in analyzed.readlines():
        analyzedappids.add(line[:-1])
    analyzed=open('analyzed_b.csv','a')
    fe=open('error_b.csv','a')
    outputfolder='output/'
    
    apkgfiles=[]
    resfile=open('AIAPI-b.csv','a')
    # resPDGfile=open('result_PDG_b.csv','a')
    
    with open('baiduids.csv') as f:
        for line in f:
            data=line[:-1].split('.zip')
            apkgfiles.append(data[0]) # id, batch
    # with open('cmrfvuln_b.csv') as f:
    #     for line in f:
    #         wxid=line[:-1].split(',')[0]
    #         apkgfiles.append(wxid) 
    total=len(apkgfiles)
    count=0
    print('starting... total amount is '+str(total))
    start=time.time()

    trialcnt=0
    for item in apkgfiles:
        pkgid=item
        if pkgid in analyzedappids:
            print('skipped '+str(pkgid))
            count+=1
            continue
        trialcnt+=1
        task.put(("/home/allen/Minilab/baidu_smapp/smapps/",pkgid,"/home/allen/Github/SP23/DoubleX/src/output/"))
        # break

    while(count<total):
#                    res={'secrets':set(),'phone':False,'werun':False,'share':False,'group':False,'address':False}
        data = result.get(timeout=1000)
        wxid=data[0]
        res=data[1]
        # res2=data[2] # PDG results
        count+=1
        print("TIME: {} {}/{}: {}".format(time.time(),count,total,wxid))
        if(len(res)==0):
            # errorapp.write(wxid)
            continue
        if(type(res)==str):
            fe.write(res+"\n")
        else:
            try:
                print(res)
                resfile.write(wxid+";;;"+str(res)+"\n")
           
                analyzed.write(wxid+'\n')  

            except Exception as e:
                print(e)
        # if(len(res2)==0):
        #     continue
        # try:
        #     json.loads(res2)
        #     resPDGfile.write(wxid+";;;"+str(res2.decode(encoding='utf-8')))

        # except Exception as e:
        #     print(e)



    manager.shutdown()
    print('process finished after ' + format(time.time()-start,'.4f') + ' s.')

main()
