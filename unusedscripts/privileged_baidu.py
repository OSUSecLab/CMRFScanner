import os
import subprocess
from subprocess import STDOUT, check_call
from tempfile import NamedTemporaryFile
files={}
with open('cmrfvuln_b.csv') as f:
    for line in f:
        files[line.split(',')[0]]=set()
def getpkgusingapi(api,files):
    with NamedTemporaryFile() as f:
#        subprocess.check_call(['grep','-nr','.'+api+'(','output/','-l'],stdout=f,stderr=STDOUT)
        print('grep','-nr','".'+api+'("','output/','-l')
        res=os.popen('grep -nr ".'+api+'(" output/ -l').read()
        for line in res.split("\n"):
            if len(line.split('/'))<2:
               continue
            pkgid=line.split('/')[1]
            print(pkgid,api)
            files[pkgid].add(api)
           
paramlist=["request",
"uploadFile",
"send",
"saveImageToPhotosAlbum",
"saveVideoToPhotosAlbum",
"createMapContext",
"createMediaAudioPlayer",
"sendSocketMessage",
"write",
"requestPolymerPayment",
"saveImageToPhotosAlbum",
"saveVideoToPhotosAlbum",
"getVideoInfo",
"chooseVideo",
"setStorageSync",
"setStorage",
"setData"]
nonparamlist=["connectSocket",
"createInnerAudioContext",
"createAudioContext",
"getBackgroundAudioManager",
"getRecorderManager",
"getFileSystemManager",
"getUserInfo",
"login",
"chooseAddress",
"getStorageInfo",
"getStorageSync",
"getStorageInfoSync",
"getStorage",
"chooseInvoiceTitle",
"chooseInvoice",
"chooseImage",
"chooseVideo",
"createCameraContext",
"getLocation",
"openLocation"]
for api in paramlist:
    getpkgusingapi(api,files)
for api in nonparamlist:
    getpkgusingapi(api,files)
fw=open('result-priv-b-grep.csv','w')
for id in files:
    fw.write(id+";;;;;;"+str(files[id])+"\n")
