'''
[22,35,42,24,18,16,14,97]
20
12
5
11
12
'''
import json

cnt=0
tot=0

# fw=open('unchecked.csv','w')
# fw1=open('unused.csv','w')
wxids=set()
unusedwxids=set()
fw2=open('newresult.csv','w')
processed=set()
for batch in [22,35,42,24,18,16,14,97]:
# for batch in [5,11,12,20]:
# for batch in [22]:
    print(batch)
    with open("/home/allen/Github/Allen_unchecked/result-"+str(batch)+".csv") as f:
        for line in f:
            data=line[:-1].split(";;;")
            wxid=data[0]
            if wxid not in processed:
                processed.add(wxid)
                fw2.write(line)
            # try:
            #     res=json.loads(data[1])
            # except Exception as e:
            #     continue
            
            # tot+=1
            # if len(res['referrerInfo'])!=0 and wxid not in wxids:
            #     cnt+=1
            #     wxids.add(wxid)
            #     fw.write(wxid+","+str(batch)+'\n')
            # elif len(res['referrerInfo'])==0 and wxid not in wxids:
            #     fw1.write(wxid+','+str(batch)+'\n')
            # unusedwxids.add(wxid)
print(str(tot)+","+str(cnt))
