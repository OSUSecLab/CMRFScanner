import subprocess
import queue
import os
import re
import time
import requests
import traceback
from subprocess import DEVNULL, STDOUT, check_call
from multiprocessing.managers import BaseManager
import json
from tempfile import NamedTemporaryFile
import find_vuln_baidu as fv

def find_extradata_usage(walk_dir):
    for root, dirs, files in os.walk(walk_dir):
        
        for file in files:
            
            if file.endswith("min.js"):
                continue
            # if file.endswith(".js"):
            if file.endswith("app.js"):
                fn=os.path.join(root, file)
                tempf=open(fn,'r')
                lines=tempf.read()
                if 'extraData' in lines:
                    return True
                else:
                    return False
            
    return False
def main():
    print("Mini Apps Analyzer")
    class QueueManager(BaseManager):
            pass
    QueueManager.register('get_task_queue')
    QueueManager.register('get_result_queue')
    
    server_addr = '127.0.0.1'
    print('Connect to server %s...' % server_addr)
    print("?")
    m = QueueManager(address=(server_addr, 5000), authkey=b'abc')
    m.connect()
    task = m.get_task_queue()
    result = m.get_result_queue()


    while True:
#        try:
        starttime=int(time.time()*1000)

        miniappinfo = task.get(timeout=10)
        print("!!",miniappinfo)
        miniappfolder=miniappinfo[0]
        
        pkgid=miniappinfo[1]
        outputfolder=miniappinfo[2]
        # filefolder=miniappfolder+'/'+wxid+'-dec/'
#        f=wxid+'-dec.wxapkg'
        try:
            with NamedTemporaryFile() as f:
                t=time.time()
                subprocess.check_call(['unzip','-qq',miniappfolder+pkgid+".zip",'-d',outputfolder])
                # used=find_extradata_usage(outputfolder+"/"+pkgid)
                unpct=time.time()-t
                # if used:
                #     try:
                #         res=fv.analyze_from_wxapkg(pkgid)
                #     except Exception as e:
                #         res="err,"+pkgid+","+traceback.format_exc()
                #         result.put((pkgid,res))
                # else:
                #     res={'wxid':pkgid,'res':'NOUSE','exec_time':0}
                try:
                    res=subprocess.check_call(['node','PDG-AIAPI.js',outputfolder+pkgid],stdout=f,stderr=STDOUT)
                    f.seek(0)
                    
                    originres=f.read()
                    res=json.loads(originres.decode('utf-8'))
                    print("!!!!!",res['privilegefunclist'])

                    #res=fv.analyze_from_wxapkg(pkgid)
                    if type(res)!=str:
                        reformedres={}
                        # reformedres['batch']=res['batch']
                        reformedres['res']=res['privilegefunclist']
                        reformedres['wxid']=pkgid
                   
        #            returninfo = subprocess.Popen("sudo python3 unpack-wxapkg.py " + outputfolder+wxid+'-dec.wxapkg '+wxid+'-dec/', stdout=subprocess.PIPE, shell=True, stderr=DEVNULL)
                        print(reformedres)
                        result.put((pkgid,reformedres))

                except Exception as e:
                    print("ERROR!",traceback.format_exc())
                    print(originres)
                    res="err,"+pkgid+","+traceback.format_exc()
                    # exit()
                    result.put((pkgid,res))
                 
                
                # res['unpack_time']=unpct
                # res2={}
                # res={}
                # res2=subprocess.check_call(['node', 'PDG.js',outputfolder+pkgid], stdout=f, stderr=STDOUT)
                # f.seek(0)
                # res2=f.read()
                subprocess.check_call(['rm','-rf',outputfolder+pkgid+'/'])
                subprocess.check_call(['rm','-rf',outputfolder+pkgid+'.zip'])

                    
                    
#            returninfo = subprocess.Popen("sudo python3 unpack-wxapkg.py " + outputfolder+wxid+'-dec.wxapkg '+wxid+'-dec/', stdout=subprocess.PIPE, shell=True, stderr=DEVNULL)
                # print(res2)
                # result.put((pkgid,res,res2))
        except BrokenPipeError as b:
            print("finished")
            break
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            continue

main()
