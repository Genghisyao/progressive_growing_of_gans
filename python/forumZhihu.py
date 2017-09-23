# -*- coding:utf-8 -*-
import random
import os
import re
import time
import json
import requests
import cookielib
from db_init import *
from bs4 import BeautifulSoup
from gevent import monkey, pool
import gevent
monkey.patch_all()
pool = pool.Pool(10)

class zhihu():

    def __init__(self):
        self.user_name = None
        self.pass_word = None
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.result = list()
        self.url_list = list()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'})
        # self.session.headers.update({'Cookie': 'd_c0="AABCsWd-HwyPTsVo6baZXMEfmUhj4R37x9k=|1501051941";'})
        self.site = 'zhihu.com'  # 搜索站点
        self.url_base = 'https://www.zhihu.com'
        self.url_login_num = 'https://www.zhihu.com/login/phone_num'
        self.url_search = 'https://www.zhihu.com/r/search'
        # self.path_root = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".")  # 根节点路径
        # self.path_conf = self.path_root + '\\' + 'conf' + '\\'  # conf目录
        self.path_root = os.getcwd()  # linux根节点路径
        self.path_conf = self.path_root + '/' + 'conf' + '/'  # linux conf目录
        self.filename = "zhihu_cookies.txt"

    def save_cookies_lwp(self, cookiejar, filename):
        """
        保存cookies到本地
        """
        lwp_cookiejar = cookielib.LWPCookieJar()
        for c in cookiejar:
            args = dict(vars(c).items())
            args['rest'] = args['_rest']
            del args['_rest']
            c = cookielib.Cookie(**args)
            lwp_cookiejar.set_cookie(c)
        lwp_cookiejar.save(filename, ignore_discard=True)

    def load_cookies_from_lwp(self, filename):
        """
        读取本地cookies
        """
        lwp_cookiejar = cookielib.LWPCookieJar()
        lwp_cookiejar.load(filename, ignore_discard=True)
        return lwp_cookiejar

    def get_xsrf(self):
        """
        获取xsrf值
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'Upgrade-Insecure-Requests': '1'
        }
        response = self.session.get(self.url_base, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        xsrf = soup.find('input', attrs={"name": "_xsrf"}).get("value")
        return xsrf

    def login_num(self, user_name, pass_word):
        """
        使用电话号码登录
        :param user_name: 用户手机号码
        :param pass_word: 密码
        :return:
        """
        self.user_name = user_name
        self.pass_word = pass_word
        xsrf = self.get_xsrf()
        data = {
            "phone_num": user_name,
            "password": pass_word,
            "_xsrf": xsrf,
            "captcha_type": "cn",
        }
        content_length = len("phone_num"+"password"+"_xsrf"+"captcha_type"+"captcha")+len(user_name+pass_word+xsrf+data["captcha_type"])
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Length': str(content_length),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'd_c0="AABCsWd-HwyPTsVo6baZXMEfmUhj4R37x9k=|1501051941";',
            'Host': 'www.zhihu.com',
            'Origin': 'https://www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Xsrftoken': xsrf
        }
        response = self.session.post(self.url_login_num, data=data, headers=headers)
        login_code = response.json()
        if login_code['msg'] == u'登录成功':
            self.save_cookies_lwp(response.cookies, self.path_conf + self.filename)  # 保存cookies到本地
            print(login_code['msg'])
        else:
            print '登录失败'
            print login_code['msg']

    def is_login(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/inbox',
            'Upgrade-Insecure-Requests': '1',
        }
        # 通过个人中心页面返回状态码来判断是否为登录状态
        inbox_url = "https://www.zhihu.com/inbox"
        # allow_redirects使重定向为false
        response = self.session.get(inbox_url, headers=headers, allow_redirects=False)
        if response.status_code != 200:
            return False
        else:
            return True

    def get_index_html(self, query, page):
        """
        获取查询页面第N页源码
        :param query: 查询内容
        :param page: 第N页
        :return: 第N页源码
        """
        params = {
            'q': query,
            'offset': page*10,
            'correction': 1,
            'type': 'content',
            'range': '3m',  # 时间：3m/1d/1w/空
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/search',
            'Upgrade-Insecure-Requests': '1',
            'X-Requested-With': 'XMLHttpRequest'
        }
        # html = self.session.get(self.url_search, params=params, headers=headers, cookies=self.load_cookies_from_lwp(self.path_conf + self.filename))  # 加载本地cookies
        html = self.session.get(self.url_search, params=params, headers=headers)
        # html = self.session.get(self.url_search, params=params)
        html_json = json.loads(html.text)
        # print html_json['htmls']
        return html_json['htmls']

    def get_url(self):
        for i in range(0, 6):
            html = self.get_index_html('中山大学',i)  # 第i页源码
            sleeptime = random.uniform(2, 4)
            time.sleep(sleeptime)
            for j in html:
                soup = BeautifulSoup(j, 'html.parser')
                url = soup.find('a').attrs['href']
                if 'question' in url:
                    url = self.url_base + url  # 查询结果url
                    self.url_list.append(url)
                    # print url

    def get_question(self, url):
        print url
        article_url = url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/search',
            'Upgrade-Insecure-Requests': '1',
        }
        mid = re.findall(r'question/(\d+)', article_url)[0]
        html = self.session.get(article_url, headers=headers)
        soup = BeautifulSoup(html.text, 'lxml')
        main = soup.find('div', attrs={'id': "data"}).attrs['data-state']
        main = json.loads(main)
        main = main['entities']['questions'][mid]
        add_datetime = self.t
        channeltype = 'luntan'
        channel = self.site
        title = main['title'].replace("'", "''").replace("%", "\%").replace(":", "\:")
        Tcontent = main['editableDetail']
        content = BeautifulSoup(Tcontent, 'html.parser').text.replace("'", "''").replace("%", "\%").replace(":", "\:")
        author_id = main['author']['id']
        author_name = main['author']['name']
        Tpublish_datetime = main['created']
        publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Tpublish_datetime))
        reply_count = main['commentCount']
        read_count = main['visitCount']
        like_count = 'NULL'
        collect_count = main['followerCount']
        forward_count = 'NULL'
        # print mid, article_url, add_datetime, channeltype, channel, title, content, author_id, author_name,\
        #         publish_datetime, reply_count, read_count, like_count, collect_count, forward_count
        data = [mid, article_url, add_datetime, channeltype, channel, title, content, author_id, author_name,
                publish_datetime, reply_count, read_count, like_count, collect_count, forward_count]
        if data not in self.result and publish_datetime > '2017-01-01':
            self.result.append(data)

    def get_answer(self, url):
        print url
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/search',
            'Upgrade-Insecure-Requests': '1',
        }
        mid = re.findall(r'question/(\d+)', url)[0]
        # html = self.session.get(url, headers=headers)
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, 'lxml')
        data = soup.find('div', {'id':"data"})
        print json.loads(data.attrs['data-state'])['token']
        # id = re.findall(r'question/(\d+)', url)[0]
        # url_answer = 'https://www.zhihu.com/api/v4/questions/' + id + '/answers'
        # page = 0
        # while page <= 1:
        #     params = {
        #         'sort_by': 'default',
        #         'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[*].mark_infos[*].url;data[*].author.follower_count,badge[?(type=best_answerer)].topics',
        #         'limit': '20',
        #         'offset': page,
        #     }
        #     headers = {
        #         'accept': 'application/json, text/plain, */*',
        #         'Accept-Encoding': 'gzip, deflate, br',
        #         'Accept-Language': 'zh-CN,zh;q=0.8',
        #         'authorization': '',
        #         'Connection': 'keep-alive',
        #         'Host': 'www.zhihu.com',
        #         'Referer': url,
        #         'X-UDID': '',
        #     }
        #     html = self.session.get(url_answer, params=params, headers=headers)
        #     html = html.json()
        #     print html
        #     page += 1
        #     if html['paging']['totals'] > 0:
        #         main = html['data']
        #         for i in main:
        #             mid = id + ';' + str(i['id'])
        #             article_url = url
        #             add_datetime = self.t
        #             channeltype = 'luntan'
        #             channel = 'zhihu.com'
        #             title = i['question']['title'].replace("'", "''").replace("%", "\%").replace(":", "\:")
        #             Tcontent = i['content']
        #             content = BeautifulSoup(Tcontent, 'html.parser').text.replace("'", "''").replace("%", "\%").replace(":", "\:")
        #             author_id = i['author']['id']
        #             author_name = i['author']['name']
        #             Tpublish_datetime = i['created_time']
        #             publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(Tpublish_datetime))
        #             reply_count = i['comment_count']
        #             read_count = 'NULL'
        #             like_count = i['voteup_count']
        #             collect_count = 'NULL'
        #             forward_count = 'NULL'
        #             # print mid, article_url, add_datetime, channeltype, channel, title, content, author_id, author_name, \
        #             #     publish_datetime, reply_count, read_count, like_count, collect_count, forward_count
        #             data = [mid, article_url, add_datetime, channeltype, channel, title, content, author_id,
        #                     author_name,
        #                     publish_datetime, reply_count, read_count, like_count, collect_count, forward_count]
        #             if data not in self.result and like_count>100:
        #                 self.result.append(data)
        #         if html['paging']['is_end'] == 'false':
        #             page += 20
        #         else:
        #             break
        #     else:
        #         break

    def insert_controller(self):
        self.get_url()
        print 'Total url is %s'% len(self.url_list)
        for url in self.url_list:
            # self.get_question(url)
            # self.get_answer(url)
            # break
            pool.spawn(self.get_question, url)
        #     # pool.spawn(self.get_answer, url)
            sleeptime = random.uniform(2, 4)
            gevent.sleep(sleeptime)
        pool.join()
        # # self.insert_text()
        self.old_insert_text()

    def insert_text(self):
        valueList = []
        if len(self.result) > 0:
            for q in self.result:
                valueList.append(
                    " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s) " %
                    (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], q[14]))
            sql = """
                INSERT INTO sa_all_article (mid, url, add_datetime, channeltype, channel, title, content, author_id,
                author_name, publish_datetime, reply_count, read_count, like_count, collect_count, forward_count) VALUES
            """
            sql1 = """
                ON DUPLICATE KEY UPDATE
                reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
            """
            sql_size = 500
            if len(valueList) > 0:
                index = 0
                while index < len(valueList):
                    # print index, min(index + sql_size, len(valueList)) - 1
                    sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql1
                    session.execute(sql_insert)
                    session.commit()
                    index += sql_size

    def update_controller(self):
        sql_query = "SELECT DISTINCT url FROM sa_all_article WHERE channel = '%s'" % self.site
        query = session.execute(sql_query)
        for q in query:
            print q['url']
            pool.spawn(self.get_question, q['url'])
            pool.spawn(self.get_answer, q['url'])
            sleeptime = random.uniform(0.5, 2)
            gevent.sleep(sleeptime)
        pool.join()
        self.update_text()

    def update_text(self):
        valueList = []
        if len(self.result)>0:
            for q in self.result:
                valueList.append(
                    " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,'%s') " %
                    (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], q[14], self.t))
            sql = """
                INSERT INTO sa_all_article (mid, url, add_datetime, channeltype, channel, title, content, author_id,
                author_name, publish_datetime, reply_count, read_count, like_count, collect_count, forward_count,
                update_datetime) VALUES
            """
            sql1 = """
                ON DUPLICATE KEY UPDATE
                reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count),
                update_datetime = VALUES(update_datetime)
            """
            sql_size = 500
            if len(valueList) > 0:
                index = 0
                while index < len(valueList):
                    # print index, min(index + sql_size, len(valueList)) - 1
                    sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql1
                    session.execute(sql_insert)
                    session.commit()
                    index += sql_size

    def update_select_controller(self, event_id):
        sql_query = """
        SELECT DISTINCT url
        FROM sa_select_article
        WHERE event_id = %d AND channel = '%s'
        AND (update_datetime IS NULL OR TO_DAYS(update_datetime) - TO_DAYS(publish_datetime) < 230)
        """% (event_id, self.site)
        query = session.execute(sql_query)
        for q in query:
            print q['url']
            # pool.spawn(self.get_question, q['url'])
        #     pool.spawn(self.get_answer, q['url'])
        #     sleeptime = random.uniform(0.2, 1)
        #     gevent.sleep(sleeptime)
        # pool.join()
        # self.update_select_text(event_id)

    def update_select_text(self, event_id):
        valueList = []
        if len(self.result) > 0:
            for q in self.result:
                valueList.append(
                    " ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,'%s') " %
                    (event_id, q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], q[14],
                     self.t))
            sql = """
                        INSERT INTO sa_select_article (event_id, mid, url, add_datetime, channeltype, channel, title, content, author_id,
                        author_name, publish_datetime, reply_count, read_count, like_count, collect_count, forward_count,
                        update_datetime) VALUES
                    """
            sql1 = """
                        ON DUPLICATE KEY UPDATE
                        reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                        read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                        like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                        collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                        forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count),
                        update_datetime = VALUES(update_datetime)
                    """
            sql_size = 500
            if len(valueList) > 0:
                index = 0
                while index < len(valueList):
                    # print index, min(index + sql_size, len(valueList)) - 1
                    sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql1
                    session.execute(sql_insert)
                    session.commit()
                    index += sql_size

    def old_insert_text(self):
        valueList = []
        if len(self.result) > 0:
            for q in self.result:
                valueList.append(
                    " ('%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,'%s') " %
                    (q[1], q[0], q[5], q[2], q[9], q[7], q[8], q[13], q[11], q[10], q[12], q[6]))
            sql = """
                INSERT INTO zhihu_text (id,mid,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tfans,
                Tread,Treply,Tlike,Tcontent) VALUES
            """
            sql1 = """
                ON DUPLICATE KEY UPDATE
                Treply = IF(Treply<VALUES(Treply), VALUES(Treply), Treply),
                Tread = IF(Tread<VALUES(Tread), VALUES(Tread), Tread),
                Tlike = IF(Tlike<VALUES(Tlike), VALUES(Tlike), Tlike),
                Tfans = IF(Tfans<VALUES(Tfans), VALUES(Tfans), Tfans)
            """
            sql_size = 500
            if len(valueList) > 0:
                index = 0
                while index < len(valueList):
                    # print index, min(index + sql_size, len(valueList)) - 1
                    sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql1
                    session.execute(sql_insert)
                    session.commit()
                    index += sql_size


if __name__ == '__main__':
    print '_____start_____'
    start = time.time()
    # zhihu().login_num('15692404833', '131452Bao55')
    # print zhihu().is_login()
    # print zhihu().get_xsrf()
    # zhihu().get_url()
    zhihu().insert_controller()
    # zhihu().update_controller()
    session.close()
    end = time.time()
    print '%.4f' % (end - start)


