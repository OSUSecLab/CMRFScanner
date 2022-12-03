import json
def translateCategory(name):
    map={'时政新闻':'news','政务民生':'government','金融业':'finance','交通':'traffic','uncategorized':'uncategorized','教育':'education','效率':'efficiency','快递业与邮政':'post service','健康':'health','电商':'e-commerce','社交':'social','体育':'sports','汽车':'automobile','IT科技':'IT tech','房地产':'real estate','医疗':'medical','旅行':'travelling','游戏':'game','美食':'food','生活':'lifestyle','娱乐':'entertainment','商家自营':'shopping','工具':'tool','资讯':'information','商业服务':'business','公益':'charity'}

    return map[name]
categories=set()
cc=0
fw=open('metainfo_b.csv','w')
with open('res_b.txt','r') as f:
    for line in f:
        cc+=1
        print(cc)
        data=eval(line)
        data=data['result']
        nickname=data['title']
        wxid=data['xcx_tab_meta']['xcx_params']['xcx_appkey']
        category='uncategorized'
        if 'app_category' in data['xcx_tab_meta']:
            category=data['xcx_tab_meta']['app_category'].split(',')[-1].split("_")[0]
        if category=='':
            category='uncategorized'
        category=translateCategory(category)
        categories.add(category)
        usercount=data['click_adjust_feature']['query_click_count']
        # if 'userCount' in data['xcx_tab_meta']:
        #     userCount=data['xcx_tab_meta']['userCount']
        developer="NO_DEV"
        if 'customer_name' in data['xcx_tab_meta']:
            developer=data['xcx_tab_meta']['customer_name']
        elif 'sc_customer_name' in data['htmlData']['meta_di_info']:
            developer=data['htmlData']['meta_di_info']['sc_customer_name']
        
        devid=""
        last_upd=data['date']
        fw.write("{};;;{};;;{};;;{};;;{};;;{};;;{}\n".format(wxid,nickname,category,usercount,developer,devid,last_upd))
        # print(nickname,wxid,category,usercount,developer,devid,last_upd)
        

        
print(categories)