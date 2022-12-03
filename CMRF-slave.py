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
import find_vuln as fv
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
        batch=miniappinfo[1]
        wxid=miniappinfo[2]
        outputfolder=miniappinfo[3]
        # filefolder=miniappfolder+'/'+wxid+'-dec/'
#        f=wxid+'-dec.wxapkg'
        try:
            with NamedTemporaryFile() as f:
                t=time.time()
                subprocess.check_call(['cp',miniappfolder+wxid+"-pc.wxapkg",outputfolder])
                subprocess.check_call(['chmod','777',outputfolder+wxid+"-pc.wxapkg"])
                subprocess.check_call(['go','run','wxapkg_decrypt.go','-wxid',wxid,'-in',outputfolder+wxid+'-pc.wxapkg','-out',outputfolder+wxid+'-dec.wxapkg'])
                subprocess.check_call(['python3','unpack-wxapkg.py',outputfolder+wxid+'-dec.wxapkg'],stdout=DEVNULL)
                
                unpct=time.time()-t
                try:
                    # subprocess.check_call(['node','PDG.js',outputfolder+wxid+'-dec'])
                    res=fv.analyze_from_wxapkg(batch,wxid)
                    if type(res)!=str:
                        reformedres={}
                        reformedres['batch']=res['batch']
                        reformedres['res']=res['res']['sensitiveAPIs']
                        reformedres['wxid']=res['wxid']
                        reformedres['exec_time']=res['exec_time']
                   
        #            returninfo = subprocess.Popen("sudo python3 unpack-wxapkg.py " + outputfolder+wxid+'-dec.wxapkg '+wxid+'-dec/', stdout=subprocess.PIPE, shell=True, stderr=DEVNULL)
                        print(reformedres)
                        result.put((wxid,batch,reformedres))

                except Exception as e:
                    print(e)
                    res="err,"+wxid+","+traceback.format_exc()
                    result.put((wxid,batch,res))
                    
                # res['unpack_time']=unpct
                subprocess.check_call(['rm','-rf',outputfolder+wxid+'-dec/'])
                subprocess.check_call(['rm','-rf',outputfolder+wxid+'-dec.wxapkg'])
                subprocess.check_call(['rm','-rf',outputfolder+wxid+'-pc.wxapkg'])

                # finalresult={'batch':batch,'wxid':wxid,'res':analysis_res,'exec_time':exec_time}
        except BrokenPipeError as b:
            print("finished")
            break
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            continue

main()
