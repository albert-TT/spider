"""
Description :   mfw
Author :       albert
date:         2021/03/06
"""

import requests,time,re
from fake_useragent import UserAgent
import hashlib
from lxml import etree
import pandas as pd


ua = UserAgent(verify_ssl=False)
url = "http://www.mafengwo.cn/ajax/router.php"
headers={
    "User-Agent":ua.random,
    "Host": "www.mafengwo.cn",
}
tt =int(time.time()*1000)

def par(t):
    hl = hashlib.md5()
    hl.update(t)

    return hl.hexdigest()[2:12]

def get_page(page):
    qdata = '{"_ts":"' + str(
        tt) + '","iMddid":"12976","iPage":"'+str(page)+'","iTagId":"0","sAct":"KMdd_StructWebAjax|GetPoisByTag"}c9d6618dbc657b41a66eb0af952906f1'
    sn = par(qdata.encode('utf-8'))
    data ={
        "sAct":"KMdd_StructWebAjax|GetPoisByTag",
        "iMddid":"12976",
        "iTagId":"0",
        "iPage":str(page),
        "_ts":str(tt),
        "_sn":sn,
    }

    resp =requests.post(url,headers=headers,data=data)
    data_zm = resp.text.encode("utf-8").decode("unicode_escape").replace("\\","")

    gz1=r'<a href="(.*?)" target="_blank"'
    gz2=r'target="_blank" title="(.*?)"'
    field1 =re.findall(gz1,data_zm)
    field2 =re.findall(gz2,data_zm)
    data_dict = dict(zip(field2, field1))
    print(data_dict)
    print("第",page,"页数据抓取成功")
    return data_dict

def get_detail(page):
    data_dict = get_page(page)
    for k,v in data_dict.items():
        jq_id = v.replace("/poi/","").replace(".html","")
        for p in range(1,6):
            tts ='{"poi_id":'+jq_id+',"page":'+str(p)+',"just_comment":1}'
            qdata1='{"_ts":"'+str(tt)+'","params":"{\\"poi_id\\":\\"'+jq_id+'\\",\\"page\\":'+str(p)+',\\"just_comment\\":1}"}c9d6618dbc657b41a66eb0af952906f1'
            sn2 = par(qdata1.encode('utf-8'))
            print(sn2)
            jingqu_name =k
            headers2={
                "User-Agent":ua.random,
                # "Host": "pageet.mafengwo.cn",
                "Referer": "http://www.mafengwo.cn"+v
            }

            j_url ='http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?callback=jQuery1810036124582844795805_1614954564773&params='+tts+'&_ts='+str(tt)+'&_sn='+sn2+'&_='+str(tt)
            resp2 =requests.get(j_url,headers=headers2)

            tsl = resp2.text.replace('jQuery1810036124582844795805_1614954564773(','').replace(');','')

            tss = eval(tsl)
            sss=tss["data"]["html"]

            html = etree.HTML(sss.replace("<br \/>", ""))

            yh_name=[]
            yh_pl=[]
            plnr = html.xpath('//p[@class="rev-txt"]/text()')
            for pl in plnr:
                np =pl.replace("\n", "").replace("\r", "").replace(" ","")
                yh_pl.append(np)


            plnm = html.xpath('//a[@class="name"]/text()')

            for d in plnm:
                yd = d.replace("\n", "").replace("\r", "").replace(" ","")
                if yd !="":
                    yh_name.append(yd)

            pl_ldict = dict(zip(yh_name, yh_pl))
            print("第",p,"页抓完")
            print(pl_ldict)
            for pk,pv in pl_ldict.items():
                dict_p = {}
                list_p = []
                dict_p['景区名称'] = jingqu_name
                dict_p['用户名'] = pk
                dict_p['评论内容'] = pv
                list_p.append(dict_p)
                print(list_p)
                # data = pd.DataFrame(list_p)
                # data.to_csv(r'/Users/martin/Desktop/mfw.csv', index=False, mode='a+', encoding='utf-8')

if __name__ == '__main__':
    for i in range(2,21):
        get_detail(i)
        print("景区第",i)
    file = r"/Users/martin/Desktop/mfw.csv"
    df = pd.read_csv(file, header=0)
    datalist = df.drop_duplicates()
    datalist.to_csv(file)
    print("完成")
