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
        wxid=miniappinfo[1]
        outputfolder=miniappinfo[2]
        mode=miniappinfo[3]
        zippedfolder=miniappinfo[4]
        # filefolder=miniappfolder+'/'+wxid+'-dec/'
#        f=wxid+'-dec.wxapkg'
        try:
            with NamedTemporaryFile() as f:
                if mode=="1":
                    subprocess.check_call(['sudo','cp',miniappfolder+wxid+".zip",outputfolder])
                    subprocess.check_call(['sudo','chmod','777',outputfolder+wxid+".zip"])
                    subprocess.check_call(['unzip','-qq',outputfolder+wxid+".zip",'-d',outputfolder])
                    res=subprocess.check_call(['node', 'PDG.js',outputfolder+'output/'+wxid+"-dec/"], stdout=f, stderr=STDOUT)
                    f.seek(0)
                    res=f.read()
                    subprocess.check_call(['rm','-rf',outputfolder+'output/'+wxid+'-dec/'])
                    subprocess.check_call(['rm','-rf',outputfolder+wxid+'.zip'])
                elif mode=="2":
                    subprocess.check_call(['sudo','cp',miniappfolder+wxid+"-pc.wxapkg",outputfolder])
                    subprocess.check_call(['sudo','chmod','777',outputfolder+wxid+"-pc.wxapkg"])
                    subprocess.check_call(['go','run','wxapkg_decrypt.go','-wxid',wxid,'-in',outputfolder+wxid+'-pc.wxapkg','-out',outputfolder+wxid+'-dec.wxapkg'])
                    subprocess.check_call(['python3','unpack-wxapkg.py',outputfolder+wxid+'-dec.wxapkg'],stdout=DEVNULL)
                    subprocess.check_call(['zip','-qq','-r',outputfolder+wxid+'.zip',outputfolder+wxid+"-dec/"])
                    subprocess.check_call(['sudo','cp',outputfolder+wxid+'.zip',zippedfolder])
                    res=subprocess.check_call(['node', 'PDG.js',outputfolder+wxid+"-dec/"], stdout=f, stderr=STDOUT)
                    f.seek(0)
                    res=f.read()
                    subprocess.check_call(['rm','-rf',outputfolder+wxid+'-dec/'])
                    subprocess.check_call(['rm','-rf',outputfolder+wxid+'-dec.wxapkg'])
                    subprocess.check_call(['rm','-rf',outputfolder+wxid+'-pc.wxapkg'])
                    subprocess.check_call(['rm','-rf',outputfolder+wxid+'.zip'])

                    
                    
#            returninfo = subprocess.Popen("sudo python3 unpack-wxapkg.py " + outputfolder+wxid+'-dec.wxapkg '+wxid+'-dec/', stdout=subprocess.PIPE, shell=True, stderr=DEVNULL)
                print(res)
                result.put((wxid,res))
        except BrokenPipeError as b:
            print("finished")
            break
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            continue

main()
