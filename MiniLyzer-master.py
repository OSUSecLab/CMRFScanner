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
#    apps = getAppsList(dir_path)
#    print(pc)
    QueueManager.register('get_task_queue', callable=lambda: task_queue)
    QueueManager.register('get_result_queue', callable=lambda: result_queue)
    manager = QueueManager(address=('', 5000), authkey=b'abc')
    manager.start()
    task = manager.get_task_queue()
    result = manager.get_result_queue()

    analyzed=open('analyzed.csv','r')
    funchecked=open("unchecked.csv",'a')
    analyzedappids=set()
    for line in analyzed.readlines():
        analyzedappids.add(line[:-1])
    analyzed=open('analyzed.csv','a')
    
    miniappfolder='/home/allen/Minilab/'
    outputfolder='output/'
    folderpostfix='42'
    wxapkgfiles=[]
    resfile=open('result.csv','a')

    print("Mode 1: copy-unzip-analysis")
    print("Mode 2: copy-decrypt-decompile-zip-copy-analysis (in progress)")
    mode=input()
    if mode=="1":
        extractedfolder=miniappfolder+'extracted/'+'wxapkgs-'+folderpostfix+'w/'
        zippedfolder=miniappfolder+'extracted/wxapkgs-'+folderpostfix+'w/'
    elif mode=="2":
        extractedfolder=miniappfolder+'wxapkgs-'+folderpostfix+"w/"
        zippedfolder=miniappfolder+'extracted/wxapkgs-'+folderpostfix+'w/'

    with open(miniappfolder+'idindexs/wxids-'+folderpostfix+'.csv') as f:
        for line in f:
            wxapkgfiles.append(line[:-1])

    total=len(wxapkgfiles)
    count=0
    print('starting... total amount is '+str(total))
    start=time.time()
    for wxid in wxapkgfiles:
#        count+=1
        if wxid in analyzedappids:
            print('skipped '+str(wxid))
            count+=1
            continue
        task.put((extractedfolder,wxid,outputfolder,mode,zippedfolder))
#    print(task.get(timeout=1000))

    while(count<total):
#                    res={'secrets':set(),'phone':False,'werun':False,'share':False,'group':False,'address':False}
        data = result.get(timeout=100)
        wxid=data[0]
        res=data[1]
        count+=1;
        print("{}/{}: {}".format(count,total,wxid))
        if(len(res)==0):
            errorapp.write(wxid)
            continue
        try:
            json.loads(res)
            resfile.write(wxid+";;;"+str(res.decode(encoding='utf-8')))
            analyzed.write(wxid+'\n')  

        except Exception as e:
            print(e)


#        res={'secrets':set(),'phone':False,'share':False,'group':False,'werun':False,'address':False,'info':False,'profile':False}

#            os.system('node PDG.js {}'.format(miniappfolder+f+'/'+v+'/'+f+'-dec/'))
#            fw=open(miniappfolder+f+'/done','w')
#            fw.write('done')

#        subprocess.check_output('rm -rf {}'.format(outputfolder+wxid+"-dec/"),shell=True)
#        subprocess.check_output('rm -rf {}'.format(outputfolder+wxid+"-dec.wxapkg"),shell=True)
#        subprocess.check_output('rm -rf {}'.format(outputfolder+wxid+"-pc.wxapkg"),shell=True)
#        os.system('rm -rf {}'.format(rmfileprefix+'.wxapkg'))


    manager.shutdown()
    print('process finished after ' + format(time.time()-start,'.4f') + ' s.')

main()
