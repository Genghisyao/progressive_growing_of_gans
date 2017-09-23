# -*- coding:utf-8 -*-
import json
import random
import sys
import requests
import time
import re
import math
from bs4 import BeautifulSoup
from gevent.queue import Queue

newsText_queue = Queue()
luntanUrl_queue = Queue()
luntanText_queue = Queue()
tiebaUrl_queue = Queue()
tiebaText_queue = Queue()
zhihuUrl_queue = Queue()
zhihuText_queue = Queue()
allComm_queue = Queue()
reload(sys)  # 默认值为ANSCII，修改为utf8进行字符串解码
sys.setdefaultencoding('utf8')

def download(url, encoding=False, data=None, cookies='', json=False, timeout=10, sleep=[1.5,2.5], retry=3, addr=False):
    try:
        s = requests.session()
        user_agent = [
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2595.400 QQBrowser/9.6.10872.400",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;  Trident/5.0)",
            ]
        randdom_header = random.choice(user_agent)
        headers = {
            'Cookie': cookies,
            'User-Agent': randdom_header,
        }
        time.sleep(random.uniform(sleep[0], sleep[1]))
        # if cookies:
        #     if isinstance(cookies, dict):
        #         r = s.get(url, data, timeout=timeout, headers=headers, cookies=cookies)
        #     else:
        #         #字符串形式的cookies转换成字典形式
        #         dic_cookies = {}
        #         for line in cookies.split(';'):
        #             name, value = line.split('=', 1)
        #             dic_cookies[name] = value
        #         r = s.get(url, data, timeout=timeout, headers=headers, cookies=dic_cookies)
        # else:
        #     r = s.get(url, data, timeout=timeout, headers=headers)
        r = s.get(url, params=data, timeout=timeout, headers=headers)
        if encoding:
            r.encoding = encoding
        if addr:
            if json:
                return {'url':r.url, 'html':r.json()}
            else:
                return {'url':r.url, 'html':r.text}
        else:
            if json:
                return r.json()
            else:
                return r.text
    except Exception, e:
        if retry < 1:
            print 'Exception :', e
            return None
        else:
            return download(url=url, encoding=encoding, data=data, json=json, timeout=timeout, retry=retry-1, addr=addr, cookies=cookies)

def get_ip_address(ip):
    url1 = 'http://ip.taobao.com/service/getIpInfo.php?ip='
    url2 = 'http://ip.taobao.com/service/getIpInfo2.php?ip='
    url = random.choice([url1,url2])
    if '*' in ip:
        ip = ip.replace('*', '0')
    u = url + ip
    cookies = 'thw=cn; PHPSESSID=r1308s6fujg00i80sp7j7er9r4'
    try:
        html = download(u, json=True, timeout=0.5, sleep=[0.1, 0.2], retry=10, cookies=cookies)
        main = html['data']
        country = main['country']
        region = main['region'].replace('省','').replace('市','').replace('自治','').replace('区','').replace('洲','')
        city = main['city'].replace('省','').replace('市','').replace('自治','').replace('区','').replace('洲','')
        address = [country, region, city]
        # print ';'.join(address)
        address = ';'.join(address)
        return address
    except:
        return ''

class Baidu_crawl():
    """
    爬取————百度
    """
    def __init__(self, query, site, starttime, endtime):
        self.url = 'https://www.baidu.com/s?ft=&tn=baiduadv'  #百度搜索
        self.query = query  # 搜索内容
        self.site = site  #搜索站点
        self.starttime = time.mktime(time.strptime(starttime, '%Y-%m-%d'))
        self.endtime = time.mktime(time.strptime(endtime, '%Y-%m-%d'))

    def getUrl(self):
        """
        获取搜索结果地址
        :return: url集合
        """
        intime = 'stf='+str(self.starttime)+','+str(self.endtime)+'|stftype=2'
        page = 1
        urlList = []
        while page<30:
            data = {
                'q1': '',  #任意关键字
                'q2': self.query,  #完整关键字
                'q3': '',  #包含任意关键字
                'q4': '',  #不包含关键字
                'q5': '1',  #关键词位置
                'q6': self.site,  #搜索站点
                'pn': str(page-1) + '0',  #页数
                'gpc': intime  #时间
            }
            html = download(self.url, encoding='utf-8', data=data, json=False, timeout=10, retry=3, addr=True)
            soup = BeautifulSoup(html['html'], 'html.parser')
            #url获取
            urls = soup.find('div', attrs={'id': "content_left"})
            if urls is None:
                break
            urls = urls.find_all('div', attrs={'class': "result c-container "})
            for i in urls:
                try:
                    url = i.find('h3').find('a').attrs['href']
                    # tasks.put_nowait(url)
                    urlList.append(url)
                except:
                    continue
            #翻页控制
            pages = soup.find('div', attrs={'id': "page"}).find_all('a')
            pageList = []
            for p in pages:
                pa = p.text.strip()
                pageList.append(pa)
            if str(page+1) in pageList:
                page += 1
            else:
                break
        return urlList

class TXnews_crawl():
    """
    爬取————腾讯新闻
    """
    def __init__(self):
        self.site = 'news.qq.com'  #搜索站点

    def getText(self, url):
        """
        获取新闻正文
        :param url: 新闻网址
        :return: article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent
        """
        # cookies = 'pac_uid=0_58ec8106620c1; gj_mpvid=80515918; ad_play_index=97; dsp_cookiemapping0=1492586667155; pgv_info=ssid=s9259450720; ts_last=news.qq.com/a/20170415/002007.htm; ts_refer=www.baidu.com/link; pgv_pvid=1281052383; ts_uid=1143064466; ptag=www_baidu_com|'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, addr=True)
        if html:
            article_url = html['url']
            article_url = re.findall(r'.*?\.html|.*?\.htm|.*?\.shtml|.*?\.shtm', article_url)[0]
            print article_url
            site = self.site
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'id': "Main-Article-QQ"})
            main1 = soup.find('div', attrs={'id': "Main-P-QQ"})
            if main is not None:
                Ttitle = main.find('h1').text.strip()  #标题
                Ttime = main.find('span', attrs={'class':"article-time"})  #发布时间
                Ttime1 = main.find('span', attrs={'class': "a_time"})
                Ttime2 = main.find('span', attrs={'class': "pubTime"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                elif Ttime1 is not None:
                    Ttime1 = Ttime1.text.strip()
                    Ttime = Ttime1
                elif Ttime2 is not None:
                    Ttime2 = Ttime2.text.strip()
                    Ttime = Ttime2
                else:
                    Ttime = ''
                Tauthor = main.find('span', attrs={'class':"a_source"})
                Tauthor1 = main.find('span', attrs={'class': "color-a-1"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a').text.strip()
                elif Tauthor1 is not None:
                    Tauthor1 = Tauthor1.find('a').text.strip()
                    Tauthor = Tauthor1
                else:
                    Tauthor = '-1'
                Tcontent = main.find('div', attrs={'id': "Cnt-Main-Article-QQ"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    id = re.findall(r'cmt_id = (\d+);', html['html'])[0]
                    re_url = 'http://coral.qq.com/article/'+ id +'/commentnum'
                    html1 = download(re_url, encoding='utf-8', data=None, json=True, timeout=10, retry=3)
                    Treply = html1['data']['commentnum']
                except:
                    Treply = '-1'
                finally:
                    # print article_url, site, Ttitle, Ttime, Tauthor, Treply
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])
                    # return article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent

            elif main1 is not None:
                Ttitle = soup.find('meta', attrs={'name':"Description"}).attrs['content']  # 标题
                Ttime = re.findall(r"pubtime\D+(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})\',", html['html'])
                if Ttime is not None:
                    Ttime = Ttime[0]
                    Ttime = Ttime[0] + '-' + Ttime[1] + '-' + Ttime[2] + ' ' + Ttime[3]
                else:
                    Ttime = ''
                Tauthor = re.findall(r'para = {\s+name: \"(.*)\",', html['html'])
                if Tauthor is not None:
                    Tauthor = Tauthor[0]
                else:
                    Tauthor = '-1'
                con_url = re.sub(r'\.htm\?.*', '.hdBigPic.js', article_url)
                con_html = download(con_url, encoding='gbk', data=None, json=False, timeout=10, retry=3)
                con_list = re.findall(r'<p>(.*?)</p>', con_html)
                if con_list is not None:
                    TT = []
                    for i in con_list:
                        if i.strip() not in TT:
                            TT.append(i)
                    Tcontent = ''.join(TT)
                else:
                    Tcontent = ''
                try:
                    id = re.findall(r'aid\D+(\d+)\",', html['html'])[0]
                    re_url = 'http://coral.qq.com/article/batchcommentnum'
                    data1 = {'targetid': id}
                    html1 = download(re_url, encoding='utf-8', data=data1, json=True, timeout=10, retry=3)
                    Treply = html1['data'][0]['commentnum']
                except:
                    Treply = '-1'
                finally:
                    # print article_url, site, Ttitle, Ttime, Tauthor, Treply
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])
                    # return article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent

    def getComment(self, url, event_id):
        cookies = 'pac_uid=0_58ec8106620c1; gj_mpvid=80515918; ad_play_index=97; dsp_cookiemapping0=1492586667155; pgv_info=ssid=s9259450720; ts_last=news.qq.com/a/20170415/002007.htm; ts_refer=www.baidu.com/link; pgv_pvid=1281052383; ts_uid=1143064466; ptag=www_baidu_com|'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, cookies=cookies)
        article_url = url
        print article_url
        site = self.site
        id = re.findall(r'cmt_id\D+(\d+);|aid\D+(\d+)\",', html)[0]
        for i in id:
            if i == '':
                continue
            else:
                re_url = 'http://coral.qq.com/article/' + i + '/comment'
                break
        last_commentid = '0'
        while last_commentid:
            data1 = {
                'commentid': last_commentid,
                'reqnum': '20'
            }
            html1 = download(re_url, encoding='utf-8', data=data1, json=True, timeout=10, sleep=[0.1,0.15], retry=3)
            if html1['errCode'] != 0:
                break
            if html1['data']['retnum'] == 0:
                break
            last_commentid = html1['data']['last']
            for i in html1['data']['commentid']:
                cid = i['id']
                user_id = i['userinfo']['userid']
                user_name = i['userinfo']['nick']
                user_ip = ''
                ip_address = i['userinfo']['region'].replace(':', ';').replace('市','').replace('自治','').replace('新区','').replace('区','').replace('洲','')
                if ip_address==';;':
                    ip_address = ''
                user_head = i['userinfo']['head']
                publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(i['time']))
                reply_userid = i['replyuserid']
                like_count = i['up']
                unlike_count = -1
                read_count = -1
                reply_count = i['rep']
                source_url = article_url
                content = i['content']
                channeltype = 'news'
                channel = self.site
                heat = 0
                # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                # print like_count,unlike_count,read_count,reply_count,source_url
                allComm_queue.put_nowait([event_id,cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                           reply_userid,like_count,unlike_count,read_count,reply_count,source_url,content,channeltype,channel,heat])

class WYnews_crawl():
    """
    爬取————网易新闻
    """

    def __init__(self):
        self.site = 'news.163.com'  #搜索站点

    def getText(self, url):
        """
        获取新闻正文
        :param url: 新闻网址
        :return: article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent
        """
        cookies = 'Province=020; City=020; usertrack=c+5+hljsm+B+cg5MA7YDAg==; vjuids=-7517fab.15b5c40e631.0.a042d54907b81; _ntes_nnid=5e90ea8f4ef321150e3b5d43f68870c8,1491901408828; _ntes_nuid=5e90ea8f4ef321150e3b5d43f68870c8; UM_distinctid=15b5c41b7836eb-0fd2f7e510ef22-4e45042e-100200-15b5c41b78461b; __gads=ID=18c804c9f3ead780:T=1491901995:S=ALNI_MYWNxLkcHVgXyExP9eeFcD-mj7SiQ; afpCT=1; CNZZDATA1256734798=337963631-1491900970-http%253A%252F%252Fnews.163.com%252F%7C1492767097; CNZZDATA1256336326=1559830613-1491900088-http%253A%252F%252Fnews.163.com%252F%7C1492765460; vjlast=1491901409.1492754596.11; ne_analysis_trace_id=1492768109053; vinfo_n_f_l_n3=09c375e3d4394d15.1.13.1491901408836.1492766182939.1492768266676; s_n_f_l_n3=09c375e3d4394d151492768109056'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, addr=True, cookies=cookies)
        if html:
            article_url = html['url']
            article_url = re.findall(r'.*?\.html|.*?\.htm|.*?\.shtml|.*?\.shtm', article_url)[0]
            print article_url
            site = self.site
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'class':"post_content_main"})
            main1 = soup.find('div', attrs={'class':"ep-content-main"})
            if main is not None:
                Ttitle = main.find('h1').text.strip()  # 标题
                Ttime = main.find('div', attrs={'class':"post_time_source"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',Ttime)[0]
                else:
                    Ttime = ''
                Tauthor = main.find('div', attrs={'class':"post_time_source"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a')
                    if Tauthor is not None:
                        Tauthor = Tauthor.text.strip()
                    else:
                        Tauthor = '-1'
                else:
                    Tauthor = '-1'
                Tcontent = main.find('div', attrs={'class':"post_text"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    id = re.findall(r'"docId" : "(.*)",', html['html'])[0]
                    re_url = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'+ id
                    html1 = download(re_url, encoding='utf-8', data=None, json=True, timeout=10, retry=3)
                    Treply = html1['tcount']
                except:
                    Treply = '-1'
                finally:
                    # print article_url, site
                    # print Ttitle, Ttime, Tauthor, Treply
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])
                    
            if main1 is not None:
                Ttitle = main1.find('h1').text.strip()  # 标题
                Ttime = main1.find('div', attrs={'class':"ep-time-soure cDGray"})
                Ttime1 = main1.find('div', attrs={'class':"ep-info cDGray"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',Ttime)[0]
                elif Ttime1 is not None:
                    Ttime = Ttime1.text.strip()
                    Ttime = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',Ttime)[0]
                else:
                    Ttime = ''
                Tauthor = main1.find('div', attrs={'class':"ep-time-soure cDGray"})
                Tauthor1 = main1.find('div', attrs={'class':"ep-source cDGray"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a')
                    if Tauthor is not None:
                        Tauthor = Tauthor.text.strip()
                    else:
                        Tauthor = '-1'
                elif Tauthor1 is not None:
                    Tauthor = Tauthor1.find('span')
                    if Tauthor is not None:
                        Tauthor = Tauthor.text.strip()
                        print Tauthor
                        Tauthor = re.findall(r'来源：(.*)"', Tauthor)[0]
                    else:
                        Tauthor = '-1'
                else:
                    Tauthor = '-1'
                Tcontent = main1.find('div', attrs={'id':"endText"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    id = re.findall(r'"docId" : "(.*)",', html['html'])[0]
                    re_url = 'http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'+ id
                    html1 = download(re_url, encoding='utf-8', data=None, json=True, timeout=10, retry=3)
                    Treply = html1['tcount']
                except:
                    Treply = '-1'
                finally:
                    # print article_url, site
                    # print Ttitle, Ttime, Tauthor, Treply
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])    

    def getComment(self, url, event_id):
        cookies = 'Province=020; City=020; usertrack=c+5+hljsm+B+cg5MA7YDAg==; vjuids=-7517fab.15b5c40e631.0.a042d54907b81; _ntes_nnid=5e90ea8f4ef321150e3b5d43f68870c8,1491901408828; _ntes_nuid=5e90ea8f4ef321150e3b5d43f68870c8; UM_distinctid=15b5c41b7836eb-0fd2f7e510ef22-4e45042e-100200-15b5c41b78461b; __gads=ID=18c804c9f3ead780:T=1491901995:S=ALNI_MYWNxLkcHVgXyExP9eeFcD-mj7SiQ; afpCT=1; CNZZDATA1256734798=337963631-1491900970-http%253A%252F%252Fnews.163.com%252F%7C1492767097; CNZZDATA1256336326=1559830613-1491900088-http%253A%252F%252Fnews.163.com%252F%7C1492765460; vjlast=1491901409.1492754596.11; ne_analysis_trace_id=1492768109053; vinfo_n_f_l_n3=09c375e3d4394d15.1.13.1491901408836.1492766182939.1492768266676; s_n_f_l_n3=09c375e3d4394d151492768109056'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, cookies=cookies)
        article_url = url
        print article_url
        site = self.site
        id = re.findall(r'"docId" : "(.*)",', html)[0]
        re_url = 'http://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/' + id + '/comments/newList'
        page = 0
        while page<750:
            data1 = {
                'offset': page,
                'limit': '30',
                'showLevelThreshold': '72',
                'headLimit': '1',
                'tailLimit': '2',
                'ibc': 'newspc'
            }
            html1 = download(re_url, encoding='utf8mb4', data=data1, json=True, timeout=10, sleep=[0.1,0.15], retry=3)
            totalcount = html1['newListSize']
            if totalcount == 0:
                break
            for i in html1['comments'].itervalues():
                cid = i['commentId']
                user_id = i['user']['userId']
                if user_id == 0:
                    user_name = ''
                else:
                    user_name = i['user']['nickname']
                user_ip = i['ip']
                # print user_ip
                ip_address = get_ip_address(str(user_ip))
                # print ip_address
                # ip_address = i['user']['location']
                user_head = ''
                publish_datetime = i['createTime']
                reply_userid = ''
                like_count = i['vote']
                unlike_count = i['against']
                read_count = -1
                reply_count = -1
                source_url = article_url
                content = i['content']
                channeltype = 'news'
                channel = self.site
                heat = 0
                # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                # print like_count,unlike_count,read_count,reply_count,source_url
                allComm_queue.put_nowait([event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                          reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                                          content, channeltype, channel, heat])
            page = page + 30
            # print page, totalcount
            if page > int(totalcount):
                break

class XLnews_crawl():
    """
    爬取————新浪新闻
    """

    def __init__(self):
        self.site = 'news.sina.com.cn'  #搜索站点

    def getText(self, url):
        cookies = 'U_TRS1=000000fa.9fe376b4.58573ebc.bde2f2c3; UOR=,vip.stock.finance.sina.com.cn,; vjuids=3923fcfb8.15914cd122a.0.e347599b65a6; SINAGLOBAL=183.63.92.250_1482112700.861930; SUB=_2AkMvC7H0f8NhqwJRmP4WzWzrb4xwzgnEieLBAH7sJRMyHRl-yD83qlNetRBAqqE4nv4pjjxQaUfLZo_Os-Bxsw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFZzJ6nbHTRfVEqOXp-S.5z; SGUID=1482721389362_efec0e8d; vjlast=1488765553.1489054965.10; bdshare_firstime=1492414283526; _ct_uid=58f46f61.537a7929; lxlrtst=1492423120_o; rotatecount=2; Apache=59.42.29.149_1492670298.869113; ULV=1492670299361:18:6:6:59.42.29.149_1492670298.869113:1492670298484; afpCT=1; CNZZDATA1252916811=1442218969-1492654141-http%253A%252F%252Fnews.sina.com.cn%252F%7C1492664941; UM_distinctid=15b8a154522e79-0a3f79bddc9d05-4e45042e-100200-15b8a154523a49; CNZZDATA5399792=cnzz_eid%3D349789736-1492650802-http%253A%252F%252Fnews.sina.com.cn%252F%26ntime%3D1492667002; U_TRS2=00000095.1c285e96.58f85761.e07aa962; lxlrttp=1492423120'
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True, cookies=cookies)
        if html:
            article_url = html['url']
            article_url = re.findall(r'.*?\.html|.*?\.htm|.*?\.shtml|.*?\.shtm', article_url)[0]
            print article_url
            date = re.findall(r'/(\d{4}-\d{2}-\d{2})/', article_url)
            if len(date) == 0:
                return None
            if date[0] < '2015-07-01':
                html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, addr=True,cookies=cookies)
            site = self.site
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'class':"wrap-inner"})
            main1 = soup.find('div', attrs={'class': "Main clearfix"})
            if main is not None:
                Ttitle = main.find('h1', attrs={'id':"artibodyTitle"}).text.strip()  # 标题
                Ttime = main.find('span', attrs={'class':"time-source"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2}).*',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                else:
                    Ttime = ''
                Tauthor = soup.find('span', attrs={'class':"time-source"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a')
                    if Tauthor is not None:
                        Tauthor = Tauthor.text.strip()
                    else:
                        Tauthor = '-1'
                else:
                    Tauthor = '-1'
                Tcontent = main.find('div', attrs={'id':"artibody"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    channel = re.findall(r"channel: '(.*)',", html['html'])[0]
                    newsid = re.findall(r"newsid: '(.*)',", html['html'])[0]
                    data = {
                        'format': 'js',
                        'channel': channel,
                        'newsid': newsid,
                        'group': '',
                        'compress': '1',
                        'ie': 'gbk',
                        'oe': 'gbk',
                        'page': '1',
                        'page_size': '20'
                    }
                    re_url = 'http://comment5.news.sina.com.cn/page/info'
                    html1 = download(re_url, encoding='utf-8', data=data, json=False, timeout=10, retry=3, addr=False)
                    html1 = re.sub(r'(.*=)\{', '{', html1)
                    html1 = json.loads(html1)
                    totalcount = html1['result']['count']['show']
                    Treply = totalcount
                except:
                    Treply = '-1'
                finally:
                    # print Ttitle, Ttime, Tauthor, Treply
                    # print Tcontent
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

            elif main1 is not None:
                Ttitle = main1.find('h1', attrs={'id': "artibodyTitle"}).text.strip()  # 标题
                Ttime = main1.find('span', attrs={'id':"pub_date"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                else:
                    Ttime = ''
                Tauthor = main1.find('span', attrs={'id': "media_name"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a').text.strip()
                else:
                    Tauthor = '-1'
                Tcontent = main1.find('div', attrs={'id': "artibody"}).text.strip()
                Tcontent = re.sub(r'\n|\t', '', Tcontent)
                try:
                    channel = re.findall(r"channel: '(.*)',", html['html'])[0]
                    newsid = re.findall(r"newsid: '(.*)',", html['html'])[0]
                    data = {
                        'format': 'js',
                        'channel': channel,
                        'newsid': newsid,
                        'group': '',
                        'compress': '1',
                        'ie': 'gbk',
                        'oe': 'gbk',
                        'page': '1',
                        'page_size': '20'
                    }
                    re_url = 'http://comment5.news.sina.com.cn/page/info'
                    html1 = download(re_url, encoding='utf-8', data=data, json=False, timeout=10, retry=3, addr=False)
                    html1 = re.sub(r'(.*=)\{', '{', html1)
                    html1 = json.loads(html1)
                    totalcount = html1['result']['count']['show']
                    Treply = totalcount
                except:
                    Treply = '-1'
                finally:
                    # print Ttitle, Ttime, Tauthor, Treply
                    # print Tcontent
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

    def getComment(self, url, event_id):
        html = download(url, encoding='utf-8', data=False, json=False, timeout=10, retry=3, addr=True)
        article_url = url
        print article_url
        site = self.site
        c = re.findall(r"channel: '(.*)',", html['html'])[0]
        newsid = re.findall(r"newsid: '(.*)',", html['html'])[0]
        page = 1
        # print channel, newsid
        while page<30:
            data = {
                'channel': c,
                'newsid': newsid,
                'group': '',
                'compress': '1',
                'ie': 'gbk',
                'oe': 'gbk',
                'page': page,
                'page_size': '20'
            }
            re_url = 'http://comment5.news.sina.com.cn/page/info'
            html1 = download(re_url, encoding='utf-8', data=data, json=True, timeout=10, sleep=[0.1,0.15], retry=3, addr=True)
            # print html1['url']
            totalcount = html1['html']['result']['count']['show']
            if totalcount == 0:
                break
            cmntlist = html1['html']['result']['cmntlist']
            for i in cmntlist:
                cid = i['mid']
                user_id = i['uid']
                user_name = i['nick']
                user_ip = i['ip']
                ip_address = get_ip_address(str(user_ip))
                # ip_address = ''
                user_head = ''
                publish_datetime = i['time']
                reply_userid = ''
                like_count = i['agree']
                unlike_count = -1
                read_count = -1
                reply_count = -1
                source_url = article_url
                content = i['content']
                channeltype = 'news'
                channel = self.site
                heat = 0
                # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                # print like_count,unlike_count,read_count,reply_count,source_url
                allComm_queue.put_nowait([event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                          reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                                          content, channeltype, channel, heat])
            page = page + 1
            totalpage = math.ceil(totalcount / 20.0)
            if totalpage < page:
                break

class FHnews_crawl():
    """
    爬取————凤凰新闻
    """

    def __init__(self):
        self.site = 'news.ifeng.com'  #搜索站点

    def getText(self, url):
        """
        获取新闻正文
        :param url: 新闻网址
        :return: article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent
        """
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True)
        if html:
            article_url = html['url']
            article_url = re.findall(r'.*?\.html|.*?\.htm|.*?\.shtml|.*?\.shtm', article_url)[0]
            print article_url
            site = self.site
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'class':"Acon wrapperllb"})
            main1 = soup.find('div', attrs={'id':"artical"})
            if main is not None:
                Ttitle = main.find('h1').text.strip()  # 标题
                Ttime = main.find('span', attrs={'class':"Arial"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]
                else:
                    Ttime = ''
                Tauthor = main.find('div', attrs={'class':"Slogo wrapIphone"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('span').find('a').text.strip()
                else:
                    Tauthor = '-1'
                Tcontent = main.find('div', attrs={'class':"wrapIphone AtxtType01"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    id = re.findall(r'"commentUrl":"(.*)",', html['html'])
                    if id:
                        id = id[0]
                    else:
                        id = article_url
                    data1 = {
                        'callback':'getCmtNumCallBack',
                        'doc_url': id,
                        'job': '14',
                        'callback': 'getCmtNumCallBack'
                    }
                    re_url = 'http://comment.ifeng.com/get.php'
                    html1 = download(re_url, encoding='gbk', data=data1, json=True, timeout=10, retry=3)
                    Treply = html1['count']
                except:
                    Treply = '-1'
                finally:
                    # print Ttitle, Ttime, Tauthor, Treply
                    # print Tcontent
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

            elif main1 is not None:
                Ttitle = main1.find('h1').text.strip()  # 标题
                Ttime = main1.find('div', attrs={'id':"artical_sth"})
                if Ttime is not None:
                    Ttime = Ttime.find('span').text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D (.*)',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                else:
                    Ttime = ''
                Tauthor = main1.find('div', attrs={'id':"artical_sth"}).find('a')
                if Tauthor is not None:
                    Tauthor = Tauthor.text.strip()
                else:
                    Tauthor = '-1'
                Tcontent = main1.find('div', attrs={'id':"main_content"})
                Tcontent1 = main1.find('div', attrs={'id': "artical_real"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                elif Tcontent1 is not None:
                    Tcontent1 = Tcontent1.text.strip()
                    Tcontent = Tcontent1
                else:
                    Tcontent = ''
                Tcontent = re.sub(r'\n|\t', '', Tcontent)
                try:
                    id = re.findall(r'"commentUrl":"(.*)",', html['html'])
                    if id:
                        id = id[0]
                    else:
                        id = article_url
                    data1 = {
                        'callback': 'getCmtNumCallBack',
                        'doc_url': id,
                        'job': '14',
                        'callback': 'getCmtNumCallBack'
                    }
                    re_url = 'http://comment.ifeng.com/get.php'
                    html1 = download(re_url, encoding='gbk', data=data1, json=True, timeout=10, retry=3)
                    Treply = html1['count']
                except:
                    Treply = '-1'
                finally:
                    # print Ttitle, Ttime, Tauthor, Treply
                    # print Tcontent
                    newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

    def getComment(self, url, event_id):
        """
        获取新闻评论
        :param url: 新闻网址
        :return: 列表[article_url, site, Ctime, Cid, Cname, Ctext]
        """
        article_url = url
        print article_url
        site = self.site
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True)
        id = re.findall(r'"commentUrl":"(.*)",', html['html'])
        if id:
            id = id[0]
        else:
            id = url
        # print id
        page = 1
        while page<30:
            data1 = {
                'callback': 'newCommentListCallBack',
                'orderby': '',
                'docUrl': id,
                'job': '1',
                'p': page,
                'callback': 'newCommentListCallBack'
            }
            re_url = 'http://comment.ifeng.com/get.php'
            html1 = download(re_url, encoding='gbk', data=data1, json=True, timeout=10, sleep=[0.1,0.15], retry=3)
            totalcount = html1['count']  #评论总数
            if totalcount == 0:
                break
            comments = html1['comments']
            if comments:
                for comment in comments:
                    cid = comment['comment_id']
                    user_id = comment['user_id']
                    user_name = comment['uname']
                    user_ip = comment['client_ip']
                    ip_address = get_ip_address(str(user_ip))
                    # ip_address = comment['ip_from']
                    user_head = comment['user_url']
                    publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(comment['create_time'])))
                    reply_userid = comment['parent']
                    if reply_userid:
                        reply_userid = comment['parent'][0]['user_id']
                    else:
                        reply_userid = ''
                    like_count = comment['uptimes']
                    unlike_count = -1
                    read_count = -1
                    reply_count = -1
                    source_url = article_url
                    content = comment['comment_contents']
                    channeltype = 'news'
                    channel = self.site
                    heat = 0
                    # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                    # print like_count,unlike_count,read_count,reply_count,source_url
                    allComm_queue.put_nowait([event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                              reply_userid, like_count, unlike_count, read_count, reply_count,
                                              source_url,
                                              content, channeltype, channel, heat])
                page = page + 1
                totalpage = math.ceil(totalcount / 20.0)  # 计算评论总页数，向上取整
                if totalpage < page:
                    break
            else:
                break

class PeopleNews_crawl():
    """
    爬取————人民网新闻
    """

    def __init__(self):
        self.site = 'people.com.cn'  #搜索站点

    def getText(self, url):
        """
        获取新闻正文
        :param url: 新闻网址
        :return: article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent
        """
        cookies = '_HY_lvt_c5928ed57343443aa175434a09ea2804=1492582419784; _HY_CTK_c5928ed57343443aa175434a09ea2804=0acc9a79b115c4ca1931c41e303bec28; BAIDU_SSP_lcr=https://www.baidu.com/link?url=NszYD2w_HgkPWqrzDQ3WKApYldw_9MpUVun9r-R09M7r0dh09MUwTHzG087WaJrhBwMCY-7pDfds4xjtWArRf2xh01DHOWWWd9DpBnHwZ03&wd=&eqid=84d5edfe0003dbdd0000000658f6c280; ALLYESID4=0DB901C6E627D980; sso_c=0; wdcid=5838509dcecc0a53; _people_ip_new_code=510000; UM_distinctid=15b802cdbd364d-02e7f218c26ae6-4e45042e-100200-15b802cdbd49ce; wdses=62d3f0f698d07532; sfr=1; CNZZDATA1260954200=1457761991-1492499618-null%7C1492580619; CNZZDATA1260954203=33096124-1492503288-null%7C1492578888; CNZZDATA1256327855=1768205365-1492503342-null%7C1492578947; wdlast=1492582420'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, addr=True, cookies=cookies)
        article_url = html['url']
        if 'bbs1' not in article_url:
            article_url = re.findall(r'.*?\.html|.*?\.htm|.*?\.shtml|.*?\.shtm', article_url)[0]
            print article_url
            site = self.site
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('section', attrs={'class':"left"})
            main1 = soup.find('body')
            if main is not None:
                Ttitle = main.find('h1').text.strip()  # 标题
                Ttime = main.find('span', attrs={'id':"p_publishtime"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                else:
                    Ttime = ''
                Tauthor = main.find('span', attrs={'id':"p_origin"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a').text.strip()
                else:
                    Tauthor = '-1'
                Tcontent = main.find('div', attrs={'id':"p_content"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                Treply = '-1'
                # print article_url, site, Ttitle, Ttime, Tauthor, Treply
                newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

            elif main1 is not None:
                Ttitle = main1.find('h1')  # 标题
                Ttitle1 = main1.find('div', attrs={'class':"tit1 fl"})
                if Ttitle:
                    Ttitle = Ttitle.text.strip()
                elif Ttitle1:
                    Ttitle = Ttitle1.find('h2').text.strip()
                else:
                    return None
                Ttime = main1.find('div', attrs={'class':"box01"})
                Ttime1 = main1.find('p', attrs={'class':"sou"})
                Ttime2 = main1.find('div', attrs={'class':"publishtime"})
                if Ttime is not None:
                    Ttime = Ttime.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})\D+',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                elif Ttime1 is not None:
                    Ttime = Ttime1.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})\D+',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                elif Ttime2 is not None:
                    Ttime = Ttime2.text.strip()
                    Ttime = re.findall(r'(\d{4})\D(\d{2})\D(\d{2})\D(\d{2}:\d{2})',Ttime)[0]
                    Ttime = Ttime[0]+'-'+Ttime[1]+'-'+Ttime[2]+' '+Ttime[3]
                else:
                    Ttime = ''
                Tauthor = main1.find('div', attrs={'class':"box01"})
                Tauthor1 = main1.find('p', attrs={'class':"sou"})
                if Tauthor is not None:
                    Tauthor = Tauthor.find('a').text.strip()
                elif Tauthor1 is not None:
                    Tauthor = Tauthor1.find('a').text.strip()
                else:
                    Tauthor = '-1'
                Tcontent = main1.find('div', attrs={'class':"box_con"})
                Tcontent1 = main1.find('div', attrs={'class':"show_text"})
                if Tcontent is not None:
                    Tcontent = Tcontent.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                elif Tcontent1 is not None:
                    Tcontent = Tcontent1.text.strip()
                    Tcontent = re.sub(r'\n|\t', '', Tcontent)
                else:
                    Tcontent = ''
                try:
                    bbs = main1.find('div', attrs={'class':"message"})
                    if bbs is not None:
                        bbs = bbs.find('a').attrs['href']
                        html1 = download(bbs, encoding='gbk', data=None, json=False, timeout=10, retry=3)
                        soup1 = BeautifulSoup(html1, 'html.parser')
                        Treply = soup1.find('span', attrs={'class':"replayNum"})
                        if Treply is not None:
                            Treply = Treply.text.strip()
                        else:
                            Treply = '-1'
                    else:
                        Treply = '-1'
                except:
                    Treply = '-1'
                # print Ttitle, Ttime, Tauthor, Treply
                # print Tcontent
                newsText_queue.put_nowait([article_url, site, Ttitle, Ttime, Tauthor, Treply, Tcontent])

    def getComment(self, url, event_id):
        cookies = '_HY_lvt_c5928ed57343443aa175434a09ea2804=1492582419784; _HY_CTK_c5928ed57343443aa175434a09ea2804=0acc9a79b115c4ca1931c41e303bec28; BAIDU_SSP_lcr=https://www.baidu.com/link?url=NszYD2w_HgkPWqrzDQ3WKApYldw_9MpUVun9r-R09M7r0dh09MUwTHzG087WaJrhBwMCY-7pDfds4xjtWArRf2xh01DHOWWWd9DpBnHwZ03&wd=&eqid=84d5edfe0003dbdd0000000658f6c280; ALLYESID4=0DB901C6E627D980; sso_c=0; wdcid=5838509dcecc0a53; _people_ip_new_code=510000; UM_distinctid=15b802cdbd364d-02e7f218c26ae6-4e45042e-100200-15b802cdbd49ce; wdses=62d3f0f698d07532; sfr=1; CNZZDATA1260954200=1457761991-1492499618-null%7C1492580619; CNZZDATA1260954203=33096124-1492503288-null%7C1492578888; CNZZDATA1256327855=1768205365-1492503342-null%7C1492578947; wdlast=1492582420'
        html = download(url, encoding='gbk', data=None, json=False, timeout=10, retry=3, addr=True, cookies=cookies)
        article_url = url
        print article_url
        site = self.site
        soup = BeautifulSoup(html['html'], 'html.parser')
        sid = soup.find('meta', attrs={'name':"contentid"}).attrs['content']
        sid = re.sub(r'\D', '', sid)
        bbs = 'http://bbs1.people.com.cn/postLink.do?nid='+sid
        # bbs = soup.find('div', attrs={'class': "message"})
        # if bbs:
            # bbs = bbs.find('a')
            # if bbs:
                # bbs = bbs.attrs['href']
            # else:
                # bbs = 'http://bbs1.people.com.cn/postLink.do?nid='
            # print bbs
        # else:
            # return None
        html1 = download(bbs, encoding='gbk', data=None, json=False, timeout=10, retry=3)
        soup1 = BeautifulSoup(html1, 'html.parser')
        id = soup1.find('meta', attrs={'name':"contentid"})
        if id:
            id = id.attrs['content']
            id = re.sub(r'\D', '', id)
            re_url = 'http://bbs1.people.com.cn/api/postApi.do'
            page = 1
            while page<30:
                data1 = {'action':'postDetailByParentId', 'replayPostId':id, 'pageNo':page}
                html2 = download(re_url, encoding='utf-8', data=data1, json=False, timeout=10, sleep=[0.1,0.15], retry=3)
                html2 = re.sub(r'\\\\\\', '', html2)
                html2 = re.sub(r'"\[\\"', '[', html2)
                html2 = re.sub(r'\\"\]"', ']', html2)
                html2 = re.sub(r'\\",\\"', ',', html2)
                html2 = json.loads(html2)
                totalCount = html2['totalCount']
                if totalCount == 0:
                    break
                replayPosts = html2['replayPosts']
                if replayPosts:
                    for i in replayPosts:
                        cid = i['id']
                        user_id = i['userId']
                        user_name = i['userNick']
                        user_ip = i['userIP']
                        ip_address = get_ip_address(str(user_ip))
                        # ip_address = ''
                        user_head = ''
                        publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(i['createTime'])/1000))
                        reply_userid = i['parentId']
                        like_count = i['vote_yes']
                        unlike_count = i['vote_no']
                        read_count = i['readCount']
                        reply_count = i['replyCount']
                        source_url = article_url
                        content = i['contentText']
                        channeltype = 'news'
                        channel = self.site
                        heat = 0
                        # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                        # print like_count,unlike_count,read_count,reply_count,source_url
                        allComm_queue.put_nowait(
                            [event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                             reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                             content, channeltype, channel, heat])
                    pageCount = html2['pageCount']  # 评论总页数
                    if pageCount == page:
                        break
                    page = page + 1  #评论页数+1
                else:
                    break

class luntan_crawl():
    """
    爬取————论坛
    """
    def __init__(self, query):
        self.site = 'bbs.tianya.cn'
        self.url = 'http://search.tianya.cn/bbs?&s=4&f=3'
        self.query = query

    def getUrl(self, page):
        data = {
            'q': self.query,
            'pn': page
        }
        html = download(self.url, encoding='utf-8', data=data, json=False, timeout=10, retry=3)
        soup = BeautifulSoup(html,'html.parser')
        urls = soup.find('div', attrs={'class':"searchListOne"}).find_all('li')[:]
        for i in urls:
            try:
                url = i.find('h3').find('a').attrs['href']
            except:
                continue
            luntanUrl_queue.put_nowait(url)

    def getText(self, url):
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True)
        article_url = html['url']
        print article_url
        soup = BeautifulSoup(html['html'], 'html.parser')
        main = soup.find('div', attrs={'id': "bd"})
        main1 = soup.find('div', attrs={'class':"wd-question"})
        if main:
            Ttitle = main.find('h1').find('span').text
            Ttime = main.find('div', attrs={'class': "atl-info"}).find_all('span')[1].text.strip()
            Ttime = re.sub(u'[\u4e00-\u9fa5]+：', '', Ttime)
            Tid = main.find('div', attrs={'class': "atl-info"}).find_all('span')[0].find('a').attrs['uid'].strip()
            Tauthor = main.find('div', attrs={'class': "atl-info"}).find_all('span')[0].find('a').attrs['uname'].strip()
            Tclick = main.find('div', attrs={'class': "atl-info"}).find_all('span')[2].text.strip()
            Tclick = re.sub(u'[\u4e00-\u9fa5]+：', '', Tclick)
            Tclick = int(Tclick)
            Treply = main.find('div', attrs={'class': "atl-info"}).find_all('span')[3].text.strip()
            Treply = re.sub(u'[\u4e00-\u9fa5]+：', '', Treply)
            Treply = int(Treply)
            Tcontent = main.find('div', attrs={'class': "bbs-content clearfix"}).text.strip()
            # print article_url, Ttitle
            # print Ttime, Tid, Tauthor, Tclick, Treply
            luntanText_queue.put_nowait([article_url, Ttitle, Ttime, Tid, Tauthor, Tclick, Treply, Tcontent])

        elif main1:
            Ttitle = main1.find('h1').find('span').text
            Ttime = main1.find('div').attrs['js_replytime']
            Ttime = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', Ttime)[0]
            Tid = main1.find('div').attrs['_host']
            Tauthor = main1.find('div', attrs={'class': "q-info"}).find('a').text
            Tclick = main1.find('div').attrs['js_clickcount']
            Treply = main1.find('div').attrs['js_powerreply']
            Tcontent = main1.find('div', attrs={'class':"q-content atl-item"})
            if Tcontent:
                Tcontent = Tcontent.find('div', attrs={'class':"text"}).text.strip()
            else:
                Tcontent = ''
            # print Ttitle, Ttime, Tid, Tauthor, Tclick, Treply
            # print Tcontent
            luntanText_queue.put_nowait([article_url, Ttitle, Ttime, Tid, Tauthor, Tclick, Treply, Tcontent])

    def getComment(self, url, event_id):
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3)
        article_url = url
        soup = BeautifulSoup(html, 'html.parser')
        comments = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['atl-item'])
        for i in comments:
            cid = i.attrs['replyid']
            user_id = i.attrs['_hostid']
            user_name = i.attrs['_host']
            user_ip = ''
            ip_address = ''
            user_head = i.find('div', attrs={'class': "atl-info"}).find('a').attrs['href']
            publish_datetime = i.attrs['js_restime']
            reply_userid = ''  #评论父id
            like_count = i.find('a', attrs={'class': "zan"}).attrs['_count']
            unlike_count = -1
            read_count = -1
            reply_count = i.find('div', attrs={'class': "atl-reply"}).find('a', attrs={'title': "插入评论"}).text.strip()
            reply_count = re.findall(r'\d+', reply_count)
            if reply_count:
                reply_count = reply_count[0]
            else:
                reply_count = 0
            source_url = article_url
            content = i.find('div', attrs={'class': "bbs-content"}).text.strip()
            channeltype = 'luntan'
            channel = self.site
            heat = 0
            # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
            # print like_count,unlike_count,read_count,reply_count,source_url
            allComm_queue.put_nowait([event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                      reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                                      content, channeltype, channel, heat])

class tieba_crawl():
    """
    爬取————百度贴吧
    """

    def __init__(self, query):
        self.site = 'tieba.baidu.com'
        self.url = 'http://tieba.baidu.com/f/search/res'
        self.query = query

    def getUrl(self, page=1):
        data = {
            'ie': 'utf-8',
            'kw': '',  # 贴吧名称
            'qw': self.query,  # 关键字
            'rn': '30',  # 显示条数
            'un': '',  # 用户名
            'only_thread': '1',
            'sm': '1',  # 按时间倒序
            'sd': '',
            'ed': '',
            'pn': page  # 页数
        }
        html = download(self.url, encoding='utf-8', data=data, json=False, timeout=10, retry=3, addr=True)
        # print html['url']
        soup = BeautifulSoup(html['html'], 'html.parser')
        main = soup.find('div', attrs={'class': "s_post_list"})
        urls = main.find_all('div', attrs={'class': "s_post"})
        for i in urls:
            try:
                url = i.find('span', attrs={'class': "p_title"}).find('a').attrs['data-tid']
                url = 'http://tieba.baidu.com/p/' + url
                tiebaUrl_queue.put_nowait(url)
            except:
                continue

    def getText(self, url):
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True)
        article_url = html['url']
        print article_url
        soup = BeautifulSoup(html['html'], 'html.parser')
        main = soup.find('div', attrs={'class': "left_section"})
        if main:
            Ttitle = main.find('div', attrs={'id': "j_core_title_wrap"}).find('h1')
            Ttitle1 = main.find('div', attrs={'id': "j_core_title_wrap"}).find('h3')
            if Ttitle:
                Ttitle = Ttitle.text.strip()
            elif Ttitle1:
                Ttitle = Ttitle1.text.strip()
            else:
                Ttitle = ''
            data_field = main.find('div', attrs={'id': "j_p_postlist"}).find('div').attrs['data-field'].strip()
            data_field = json.loads(data_field)
            Ttime = data_field['content']
            if 'date' in Ttime.keys():
                Ttime = Ttime['date']
            else:
                Ttime = main.find('div', attrs={'id': "j_p_postlist"}).find('div').find_all('span', attrs={'class': "tail-info"})[-1].text.strip()
            Tid = data_field['author']['user_id']
            Tauthor = data_field['author']['user_name']
            Treply = soup.find('li', attrs={'class': "l_reply_num"}).find('span').text.strip()
            Tcontent = main.find('div', attrs={'id': "j_p_postlist"}).find('div').find('cc').text.strip()
            # print Ttitle
            # print Ttime, Tid, Tauthor, Treply
            # print Tcontent
            tiebaText_queue.put_nowait([article_url, Ttitle, Ttime, Tid, Tauthor, Treply, Tcontent])

    def getComment(self, url, event_id):
        page = 1
        while page<=30:
            data = {'pn': page}
            html = download(url, encoding='utf-8', data=data, json=False, timeout=10, retry=3, addr=True)
            article_url = url
            # print article_url
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'class': "left_section"}).find('div', attrs={'id': "j_p_postlist"})
            if main:
                com_all = main.find_all('div', attrs={'data-field': True})
                if com_all:
                    for i in com_all[1:]:
                        data_field = i.attrs['data-field'].strip()
                        data_field = json.loads(data_field)
                        if 'content' in data_field.keys():
                            cid = data_field['content']['post_id']
                            user_id = data_field['author']['user_id']
                            user_name = data_field['author']['user_name']
                            user_ip = ''
                            ip_address = ''
                            user_head = ''
                            if 'date' in data_field['content'].keys():
                                publish_datetime = data_field['content']['date']
                            else:
                                publish_datetime = i.find_all('span', attrs={'class': "tail-info"})[-1].text.strip()
                            reply_userid = ''
                            like_count = -1
                            unlike_count = -1
                            read_count = -1
                            reply_count = data_field['content']['comment_num']
                            source_url = article_url
                            content = i.find('cc').text.strip()
                            channeltype = 'tieba'
                            channel = self.site
                            heat = 0
                            # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                            # print like_count,unlike_count,read_count,reply_count,source_url
                            allComm_queue.put_nowait(
                                [event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                 reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                                 content, channeltype, channel, heat])

            # 翻页控制
            pages = soup.find('li', attrs={'class': "l_pager pager_theme_4 pb_list_pager"}).find_all('a')
            pageList = []
            for p in pages:
                pa = p.text.strip()
                pageList.append(pa)
            if str(page + 1) in pageList:
                page += 1
            else:
                break

class zhihu_crawl():
    """
    爬取————知乎
    """
    def __init__(self,query):
        self.site = 'zhihu.com'
        self.query = query

    def getUrl(self, page):
        url_base = 'https://www.zhihu.com'
        url_first = 'https://www.zhihu.com/r/search'
        page = str(page-1) + '0'
        data = {
            'q': self.query,
            'offset': page,
            'type': 'content',
            'range': '',  #时间：3m/1d/1w/空
        }
        cookies = 'q_c1=0320f35733cf434b8e999c166308a7cd|1501051940000|1501051940000; d_c0="AABCsWd-HwyPTsVo6baZXMEfmUhj4R37x9k=|1501051941"; _zap=d791270b-4ea4-4cc4-b3ef-c59851f5bfe5; aliyungf_tc=AQAAAFA8KTUMBQYAMcVJ3yJcGsdSMg+y; _xsrf=3453ef6d59c5d373eb6a30f4a0590025; _xsrf=3453ef6d59c5d373eb6a30f4a0590025; __utma=51854390.766347949.1501051940.1501051940.1501208736.2; __utmb=51854390.0.10.1501208736; __utmc=51854390; __utmz=51854390.1501208736.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.000--|3=entry_date=20170726=1; z_c0=Mi4wQUFEQ1lGSDF4d3NBQUVLeFozNGZEQmNBQUFCaEFsVk5GaldpV1FBV1dOTkNmNnE2NDdjblRhV2NKMUg5V0JJTFhB|1501210646|96329d71f9ecc1cdbab7c62ef526fedfe216391b; r_cap_id="NDM4OWU2ZDUxMDhhNDYwM2JmM2RkNDA2NTM3NzhhNDA=|1501210646|9d1038e904176757612bbdb715f5661c8e110560"; cap_id="YjRjZjM4ODllOWQ2NDc2MGFlMWY4MDEyOTZhMDgyYzg=|1501210646|9a035194b9f78404e67f14f8321d6df70c13d185"'
        html = download(url_first, encoding='utf-8', data=data, json=True, timeout=10, retry=3, addr=True, cookies=cookies)
        # print html['url']
        if html:
            html1 = html['html']['htmls']
            if len(html1) > 0:
                for i in html1:
                    soup = BeautifulSoup(i, 'html.parser')
                    url = soup.find('a').attrs['href']
                    url = url_base + url
                    zhihuUrl_queue.put_nowait(url)

    def getText(self, url):
        cookies = '_zap=41e6a0ed-41e7-4737-8c17-5c3f8ae0971c; d_c0="ACDAqbSttQqPThLVqMstWLF1pEW3wZp4eFc=|1476770932"; _zap=d4662d8e-4b71-43c5-b38f-1c2f5f428af4; q_c1=b2292b3976c544dc85b9ca91f4006f38|1493014666000|1477553790000; _ga=GA1.2.1081220280.1495090261; _xsrf=54175a60f65bc66bb1ad0c6b02f78ec6; r_cap_id="NjM4OTM1M2U0MjA1NGE4NDk2NzhlMTJjMDdhZWMxMzQ=|1495512760|4d4f7f4c63645ccefb09a990a15d0271757639b6"; cap_id="ZTllYjkxZGMwZGJmNDNiMThhMTJjODg3ZjFiYjA1Y2Q=|1495512759|db0b63ccde6e66d9aec854be43a44a7b0b9a2b66"; l_cap_id="ODM0YjU1M2UwNTJmNGYzMmEwZThjYmQ1MjZlNmMxOTE=|1495512760|07964cc5d1318360b5e3d8d9257487c0e371a642"; __utmt=1; __utma=51854390.1081220280.1495090261.1495433614.1495512173.13; __utmb=51854390.10.10.1495512173; __utmz=51854390.1495512173.13.6.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/question/19995741; __utmv=51854390.000--|2=registration_date=20170519=1^3=entry_date=20161027=1; aliyungf_tc=AQAAALB/vwQc0AYAEsRJ3z/sCFXB9XU2; acw_tc=AQAAAG1vigyFOQkAEsRJ3+dFzUCYFvEN; capsion_ticket="2|1:0|10:1495513301|14:capsion_ticket|44:YjI0NDdhMzRiYjYyNGMyYzg3Mzk1YmI4ZGM3MDM2ZDk=|2caff611fa661256c649b292ec81b4701b597c94422ca0bddb84fa343cc76ed8"; z_c0="2|1:0|10:1495513309|4:z_c0|92:Mi4wQUFEQ1lGSDF4d3NBSU1DcHRLMjFDaVlBQUFCZ0FsVk4zVVZMV1FCcC1SSC13bmRldGM4S3h5clBhRkhPeVRiUnhR|cf3e15fa541a78cfafa235448385bbf1a238c533afb030fb3a2fc018b1aa7215"'
        html = download(url, encoding='utf-8', data=None, json=False, timeout=10, retry=3, addr=True, cookies=cookies)
        article_url = html['url']
        print article_url
        page = 0
        id = re.findall(r'question/(\d+)', article_url)
        if id:
            soup = BeautifulSoup(html['html'], 'html.parser')
            main = soup.find('div', attrs={'id': "data"}).attrs['data-state']
            # print main
            if main:
                #——————————问题——————————
                id = id[0]
                main = json.loads(main)
                main = main['entities']['questions'][id]
                key = article_url
                mid = main['id']
                Ttitle = main['title']
                Tpublic_datetime = main['created']
                Tpublic_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Tpublic_datetime))
                Tauthor_id = main['author']['id']
                Tauthor_name = main['author']['name']
                Tfans = main['followerCount']
                Tread = main['visitCount']
                Treply = main['commentCount']
                Tlike = '-1'
                Tcontent = main['editableDetail']
                Tcontent = BeautifulSoup(Tcontent, 'html.parser').text
                zhihuText_queue.put_nowait([key,mid,Ttitle,Tpublic_datetime,Tauthor_id,Tauthor_name,Tfans,Tread,Treply,Tlike,Tcontent])
                # print key,mid
                # print Ttitle
                # print add_datetime, Tpublic_datetime
                # print Tauthor_id, Tauthor_name
                # print Tfans, Tread, Treply, Tlike
                # print Tcontent
                # ——————————回答——————————
                url_ans = 'https://www.zhihu.com/api/v4/questions/' + id + '/answers'
                while page >= 0:
                    data_ans = {
                        'sort_by': 'default',
                        'include': 'data[*].is_normal, is_collapsed, collapse_reason, is_sticky, collapsed_by, suggest_edit, comment_count, can_comment, content, editable_content, voteup_count, reshipment_settings, comment_permission, mark_infos, created_time, updated_time, relationship.is_authorized, is_author, voting, is_thanked, is_nothelp, upvoted_followees;data[*].author.badge[?(type = best_answerer)].topics',
                        'limit': '20',
                        'offset': page,
                    }
                    cookies_ans = 'd_c0="ACDAqbSttQqPThLVqMstWLF1pEW3wZp4eFc=|1476770932"; _zap=d4662d8e-4b71-43c5-b38f-1c2f5f428af4; q_c1=b2292b3976c544dc85b9ca91f4006f38|1493014666000|1477553790000; _ga=GA1.2.1081220280.1495090261; _xsrf=54175a60f65bc66bb1ad0c6b02f78ec6; r_cap_id="NjM4OTM1M2U0MjA1NGE4NDk2NzhlMTJjMDdhZWMxMzQ=|1495512760|4d4f7f4c63645ccefb09a990a15d0271757639b6"; cap_id="ZTllYjkxZGMwZGJmNDNiMThhMTJjODg3ZjFiYjA1Y2Q=|1495512759|db0b63ccde6e66d9aec854be43a44a7b0b9a2b66"; l_cap_id="ODM0YjU1M2UwNTJmNGYzMmEwZThjYmQ1MjZlNmMxOTE=|1495512760|07964cc5d1318360b5e3d8d9257487c0e371a642"; aliyungf_tc=AQAAALB/vwQc0AYAEsRJ3z/sCFXB9XU2; acw_tc=AQAAAG1vigyFOQkAEsRJ3+dFzUCYFvEN; capsion_ticket="2|1:0|10:1495513301|14:capsion_ticket|44:YjI0NDdhMzRiYjYyNGMyYzg3Mzk1YmI4ZGM3MDM2ZDk=|2caff611fa661256c649b292ec81b4701b597c94422ca0bddb84fa343cc76ed8"; capsion_ticket=27ef762883d249678bd7808fd3b5f7bb; z_c0=Mi4wQUFEQ1lGSDF4d3NBSU1DcHRLMjFDaVlBQUFCZ0FsVk4zVVZMV1FCcC1SSC13bmRldGM4S3h5clBhRkhPeVRiUnhR|1495520950|f3b3625756d91d6617bfe1545df658f901c54051; s-q=%E4%B8%AD%E5%B1%B1%E5%A4%A7%E5%AD%A6; s-i=1; sid=0t4su56g; __utma=51854390.1081220280.1495090261.1495512173.1495520089.14; __utmb=51854390.7.9.1495521989537; __utmc=51854390; __utmz=51854390.1495520089.14.7.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/account/unhuman; __utmv=51854390.100--|2=registration_date=20170519=1^3=entry_date=20161027=1'
                    html = download(url_ans, encoding='utf-8', data=data_ans, json=True, timeout=10, retry=3, addr=True,
                                    cookies=cookies_ans)
                    main_ans = html['html']['data']
                    for i in main_ans:
                        mid_ans = i['id']
                        Ttitle_ans = i['question']['title']
                        Tpublic_datetime_ans = i['created_time']
                        Tpublic_datetime_ans = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Tpublic_datetime_ans))
                        Tauthor_id_ans = i['author']['id']
                        Tauthor_name_ans = i['author']['name']
                        Tfans_ans = '-1'
                        Tread_ans = '-1'
                        Treply_ans = i['comment_count']
                        Tlike_ans = i['voteup_count']
                        Tcontent_ans = i['content']
                        Tcontent_ans = BeautifulSoup(Tcontent_ans, 'html.parser').text
                        zhihuText_queue.put_nowait(
                            [key, mid_ans, Ttitle_ans, Tpublic_datetime_ans, Tauthor_id_ans, Tauthor_name_ans, Tfans_ans, Tread_ans, Treply_ans,
                             Tlike_ans, Tcontent_ans])
                        # print mid
                        # print Ttitle
                        # print add_datetime, Tpublic_datetime
                        # print Tauthor_id, Tauthor_name
                        # print Tfans, Tread, Treply, Tlike
                        # print Tcontent
                    totalpage = html['html']['paging']['totals']
                    page += 20
                    if page > int(totalpage):
                        break

    def getText2(self, url):
        key = url
        id = re.findall(r'question/(\d+)', key)
        if id:
            id = id[0]
            url = 'https://www.zhihu.com/api/v4/questions/'+ id +'/answers'
            page = 0
            while page<=500:
                data = {
                    'sort_by': 'default',
                    'include': 'data[*].is_normal, is_collapsed, collapse_reason, is_sticky, collapsed_by, suggest_edit, comment_count, can_comment, content, editable_content, voteup_count, reshipment_settings, comment_permission, mark_infos, created_time, updated_time, relationship.is_authorized, is_author, voting, is_thanked, is_nothelp, upvoted_followees;data[*].author.badge[?(type = best_answerer)].topics',
                    'limit': '20',
                    'offset': page,
                }
                cookies = 'd_c0="ACDAqbSttQqPThLVqMstWLF1pEW3wZp4eFc=|1476770932"; _zap=d4662d8e-4b71-43c5-b38f-1c2f5f428af4; q_c1=b2292b3976c544dc85b9ca91f4006f38|1493014666000|1477553790000; _ga=GA1.2.1081220280.1495090261; _xsrf=54175a60f65bc66bb1ad0c6b02f78ec6; r_cap_id="NjM4OTM1M2U0MjA1NGE4NDk2NzhlMTJjMDdhZWMxMzQ=|1495512760|4d4f7f4c63645ccefb09a990a15d0271757639b6"; cap_id="ZTllYjkxZGMwZGJmNDNiMThhMTJjODg3ZjFiYjA1Y2Q=|1495512759|db0b63ccde6e66d9aec854be43a44a7b0b9a2b66"; l_cap_id="ODM0YjU1M2UwNTJmNGYzMmEwZThjYmQ1MjZlNmMxOTE=|1495512760|07964cc5d1318360b5e3d8d9257487c0e371a642"; aliyungf_tc=AQAAALB/vwQc0AYAEsRJ3z/sCFXB9XU2; acw_tc=AQAAAG1vigyFOQkAEsRJ3+dFzUCYFvEN; capsion_ticket="2|1:0|10:1495513301|14:capsion_ticket|44:YjI0NDdhMzRiYjYyNGMyYzg3Mzk1YmI4ZGM3MDM2ZDk=|2caff611fa661256c649b292ec81b4701b597c94422ca0bddb84fa343cc76ed8"; capsion_ticket=27ef762883d249678bd7808fd3b5f7bb; z_c0=Mi4wQUFEQ1lGSDF4d3NBSU1DcHRLMjFDaVlBQUFCZ0FsVk4zVVZMV1FCcC1SSC13bmRldGM4S3h5clBhRkhPeVRiUnhR|1495520950|f3b3625756d91d6617bfe1545df658f901c54051; s-q=%E4%B8%AD%E5%B1%B1%E5%A4%A7%E5%AD%A6; s-i=1; sid=0t4su56g; __utma=51854390.1081220280.1495090261.1495512173.1495520089.14; __utmb=51854390.7.9.1495521989537; __utmc=51854390; __utmz=51854390.1495520089.14.7.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/account/unhuman; __utmv=51854390.100--|2=registration_date=20170519=1^3=entry_date=20161027=1'
                html = download(url, encoding='utf-8', data=data, json=True, timeout=10, retry=3, addr=True, cookies=cookies)
                main = html['html']['data']
                for i in main:
                    mid = i['id']
                    Ttitle = i['question']['title']
                    Tpublic_datetime = i['created_time']
                    Tpublic_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Tpublic_datetime))
                    Tauthor_id = i['author']['id']
                    Tauthor_name = i['author']['name']
                    Tfans = '-1'
                    Tread = '-1'
                    Treply = i['comment_count']
                    Tlike = i['voteup_count']
                    Tcontent = i['content']
                    Tcontent = BeautifulSoup(Tcontent, 'html.parser').text
                    zhihuText_queue.put_nowait(
                        [key, mid, Ttitle, Tpublic_datetime, Tauthor_id, Tauthor_name, Tfans, Tread, Treply,
                         Tlike, Tcontent])
                    # print mid
                    # print Ttitle
                    # print add_datetime, Tpublic_datetime
                    # print Tauthor_id, Tauthor_name
                    # print Tfans, Tread, Treply, Tlike
                    # print Tcontent
                totalpage = html['html']['paging']['totals']
                page += 20
                if page > int(totalpage):
                    break

    def getComment(self, url, event_id):
        url1 = url.split(';')[0]
        id = url.split(';')[1]
        host_id = re.findall('\d+', url1)[0]
        if host_id == id:
            url2 = 'https://www.zhihu.com/api/v4/questions/' + id + '/comments'
        else:
            url2 = 'https://www.zhihu.com/api/v4/answers/' + id + '/comments'
        # print url1
        # print url2
        page = 0
        while page<=500:
            data = {
                'include': 'data[*].author,collapsed,reply_to_author,disliked,content,voting,vote_count,is_parent_author,is_author',
                'order': 'normal',
                'limit': '20',
                'offset': page,
                'status': 'open',
            }
            cookies = 'q_c1=07500244e9aa49c4b6b57eaefd55557d|1495246849000|1495246849000; d_c0="AJBCMcX9yAuPTln-LyeGTvGrYV0uhtIgveo=|1495246858"; _zap=3577a011-cf28-4fcb-b898-99648bc25a4e; r_cap_id="Mjc4NzgzOTY3NTg4NDkwNDkyMDQ3NTc0N2FkMjE4MWY=|1497432379|9adda691bd6e341196d4cb7e261be4b5f19ec422"; cap_id="MDVkMzQ5NjAyNWUxNDg4ZGEzMDU4ODJiNWFiODk2Y2M=|1497432379|8c6e4302478a91fdcc1078ca3c4153f20c98b9e0"; l_cap_id="YjkyZWViMzYyZjJhNDM0OWIzNmRlZjdiNWQ0MjQ3OWY=|1497432578|ee02a94bdbd67fec6204a2dfcafce3715f3af0d0"; __utma=51854390.1133812831.1497432379.1497432379.1497432379.1; __utmz=51854390.1497432379.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=51854390.000--|2=registration_date=20170519=1^3=entry_date=20170520=1; capsion_ticket="2|1:0|10:1497433013|14:capsion_ticket|44:NjAxYzIzYmViMjZlNDhiOWFmODI4OTA3YzMzNTNiYmM=|3bbbdf8ea1d9687f20d66b7fdd3ff0ead6ad947e3b821db9da300553165e2d11"; z_c0="2|1:0|10:1497433026|4:z_c0|92:Mi4wQUFEQ1lGSDF4d3NBa0VJeHhmM0lDeVlBQUFCZ0FsVk53cEJvV1FCWWE1VVgxazBna3ZxUTA4NVFpVG5KZlFWWWZn|4884b8d46bd5e709e83a1c0270b1963530544fdfbac68f2c1b17aebf76e21999"'
            html = download(url2, encoding='utf-8', data=data, cookies=cookies, json=True, timeout=10, sleep=[0.5,1.5], retry=3, addr=True)
            # print html['url']
            results = html['html']['data']
            for i in results:
                cid = i['id']
                user_id = i['author']['member']['id']
                user_name = i['author']['member']['name']
                user_ip = ''
                ip_address = ''
                user_head = i['author']['member']['url']
                publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i['created_time']))
                if i.has_key('reply_to_author'):
                    reply_userid = i['reply_to_author']['member']['id']
                else:
                    reply_userid = ''
                like_count = i['vote_count']
                unlike_count = -1
                read_count = -1
                reply_count = -1
                source_url = url1
                content = i['content']
                channeltype = 'zhihu'
                channel = self.site
                heat = 0
                # print cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime, reply_userid
                # print like_count,unlike_count,read_count,reply_count,source_url
                allComm_queue.put_nowait([event_id, cid, user_id, user_name, user_ip, ip_address, user_head, publish_datetime,
                                          reply_userid, like_count, unlike_count, read_count, reply_count, source_url,
                                          content, channeltype, channel, heat])

            is_end = html['html']['paging']['is_end']
            if is_end:
                break
            else:
                page += 20


if __name__ == '__main__':
    print '_______start test_______'
    
    