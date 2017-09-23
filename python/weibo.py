# -*- coding:utf-8 -*-
import os
import random
import re
import rsa
import time
import json
import base64
import logging
import binascii
import requests
import urllib
from PIL import Image
from db_init import *
from bs4 import BeautifulSoup
from gevent import monkey, pool
import gevent
import smtplib
import time
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
monkey.patch_all()
pool = pool.Pool(10)
import cookielib

class sendCode():
    """
    发送预警
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = time.strftime('%Y%m%d', time.localtime(time.time()))

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr(( \
            Header(name, 'utf-8').encode(), \
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def sendMail(self, to_addr, subject, content, html=False):
        # subject = u'舆情预警通知'
        # content = u'中文测试'
        # to_addr = "627818082@qq.com"

        # 配置
        from_addr = '627818082@qq.com'  # 发送人邮箱
        password = 'jbaldhvlukyzbfje'  # 发送人邮箱密码
        smtp_server = 'smtp.qq.com'  # 邮箱服务器
        smtp_port = 465  # 邮箱端口号

        # 邮件对象
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = self._format_addr(u'发送人 <%s>' % from_addr)
        msg['To'] = self._format_addr(u'收件人 <%s>' % to_addr)

        # 邮件正文是MIMEText:
        if html:
            msg.attach(MIMEText(content, 'html', 'utf-8'))  # 发html邮件
        else:
            msg.attach(MIMEText(content, 'plain', 'utf-8'))  # 发纯文本邮件

        with open('captcha.jpg', 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('image', 'jpg', filename='captcha.jpg')
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename='captcha.jpg')
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)

        # server = smtplib.SMTP(smtp_server, smtp_port)  # 非ssl
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # ssl
        server.set_debuglevel(0)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()

class WeiBo(object):
    """
    class of WeiBoLogin, to login weibo.com
    """

    def __init__(self):
        self.user_name = None
        self.pass_word = None
        self.user_uniqueid = None
        self.user_nick = None
        self.site = 'weibo.com'
        self.session = requests.Session()
        agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
        self.session.headers.update({"User-Agent": agent})
        self.session.get("http://weibo.com/login.php")
        self.result = list()
        self.result_update = list()
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # self.path_root = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + ".")  # windows根节点路径
        # self.path_conf = self.path_root + '\\' + 'conf' + '\\'  # windows conf目录
        self.path_root = os.getcwd()  # linux根节点路径
        self.path_conf = self.path_root + '/' + 'conf' + '/'  # linux conf目录
        self.filename = "weibo_cookies.txt"
        return

    def login(self, user_name, pass_word):
        """
        login weibo.com, return True or False
        """
        self.user_name = user_name
        self.pass_word = pass_word
        self.user_uniqueid = None
        self.user_nick = None

        # get json data
        s_user_name = self.get_username()
        json_data = self.get_json_data(su_value=s_user_name)
        if not json_data:
            return False
        s_pass_word = self.get_password(json_data["servertime"], json_data["nonce"], json_data["pubkey"])

        # make post_data
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "userticket": "1",
            "vsnf": "1",
            "service": "miniblog",
            "encoding": "UTF-8",
            "pwencode": "rsa2",
            "sr": "1280*800",
            "prelt": "529",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "rsakv": json_data["rsakv"],
            "servertime": json_data["servertime"],
            "nonce": json_data["nonce"],
            "su": s_user_name,
            "sp": s_pass_word,
            "returntype": "TEXT",
        }

        # get captcha code
        if json_data["showpin"] == 1:
            url = "http://login.sina.com.cn/cgi/pin.php?r=%d&s=0&p=%s" % (int(time.time()), json_data["pcid"])
            with open("captcha.jpg", "wb") as file_out:
                file_out.write(self.session.get(url).content)
            sendCode().sendMail("627818082@qq.com", u'微博登录验证码', u'验证码')
            code = raw_input("请输入验证码:")
            post_data["pcid"] = json_data["pcid"]
            post_data["door"] = code

        # login weibo.com
        login_url_1 = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)&_=%d" % int(time.time())
        json_data_1 = self.session.post(login_url_1, data=post_data).json()
        if json_data_1["retcode"] == "0":
            params = {
                "callback": "sinaSSOController.callbackLoginStatus",
                "client": "ssologin.js(v1.4.18)",
                "ticket": json_data_1["ticket"],
                "ssosavestate": int(time.time()),
                "_": int(time.time()*1000),
            }
            response = self.session.get("https://passport.weibo.com/wbsso/login", params=params)
            json_data_2 = json.loads(re.search(r"\((?P<result>.*)\)", response.text).group("result"))
            if json_data_2["result"] is True:
                self.user_uniqueid = json_data_2["userinfo"]["uniqueid"]
                self.user_nick = json_data_2["userinfo"]["displayname"]
                logging.warning("WeiBoLogin succeed: %s", json_data_2)
                self.save_cookies_lwp(response.cookies, self.path_conf + self.filename)  # 保存cookies到本地
            else:
                logging.warning("WeiBoLogin failed: %s", json_data_2)
        else:
            logging.warning("WeiBoLogin failed: %s", json_data_1)
        return True if self.user_uniqueid and self.user_nick else False

    def get_username(self):
        """
        get legal username
        """
        username_quote = urllib.quote(self.user_name)
        username_base64 = base64.b64encode(username_quote.encode("utf-8"))
        return username_base64.decode("utf-8")

    def get_json_data(self, su_value):
        """
        get the value of "servertime", "nonce", "pubkey", "rsakv" and "showpin", etc
        """
        params = {
            "entry": "weibo",
            "callback": "sinaSSOController.preloginCallBack",
            "rsakt": "mod",
            "checkpin": "1",
            "client": "ssologin.js(v1.4.18)",
            "su": su_value,
            "_": int(time.time()*1000),
        }
        try:
            response = self.session.get("http://login.sina.com.cn/sso/prelogin.php", params=params)
            json_data = json.loads(re.search(r"\((?P<data>.*)\)", response.text).group("data"))
        except Exception as excep:
            json_data = {}
            logging.error("WeiBoLogin get_json_data error: %s", excep)

        logging.debug("WeiBoLogin get_json_data: %s", json_data)
        return json_data

    def get_password(self, servertime, nonce, pubkey):
        """
        get legal password
        """
        string = (str(servertime) + "\t" + str(nonce) + "\n" + str(self.pass_word)).encode("utf-8")
        public_key = rsa.PublicKey(int(pubkey, 16), int("10001", 16))
        password = rsa.encrypt(string, public_key)
        password = binascii.b2a_hex(password)
        return password.decode()

    def get_exception_code(self):
        timestamp = str(time.time()*1000) + '8'
        image_url = 'http://s.weibo.com/ajax/pincode/pin?type=sass'
        with open("pin.png", "wb") as file_out:
            image = self.session.get(image_url)
            # print image.headers
            file_out.write(image.content)
        img = Image.open('pin.png')
        img.show()
        code = raw_input("请输入验证码:")
        verified_url = 'http://s.weibo.com/ajax/pincode/verified?__rnd=' + str(time.time()*1000)
        data = {
            'secode': code,
            'type': 'sass',
            'pageid': 'weibo',
            '_t': 0
        }
        self.session.headers.update({'X-Requested-With':'XMLHttpRequest'})
        aa = self.session.post(verified_url, data)
        # print aa.headers

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

    def get_index_html(self, query, page):
        query = urllib.quote(query)
        params = {
            'scope': 'ori',  # 类型
            'suball': '1',  # 包含全部
            'timescope': 'custom:2017-01-01:',  # 时间
            'Refer': 'g',
            'page': page
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 's.weibo.com',
            'Referer': 'http://s.weibo.com/',
            'Upgrade-Insecure-Requests': '1',
        }
        index_url = 'http://s.weibo.com/weibo/'+ query  # 搜索主页+查询词
        html = self.session.get(index_url, params=params, headers=headers, cookies=self.load_cookies_from_lwp(self.path_conf + self.filename))  # 加载本地cookies
        # html = self.session.get(index_url, params=params, headers=headers)
        print html.url
        html = html.text
        lindex = html.find('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct"')
        rindex = html[lindex:].find('</script>')
        rindex = lindex + rindex - 1
        lindex = lindex + len('<script>STK && STK.pageletM && STK.pageletM.view(')
        jo = json.loads(html[lindex:rindex])
        data = jo['html']  # 实时微博页面
        # print data
        return data

    def get_html_content(self, data):
        soup = BeautifulSoup(data, 'lxml')
        root_1 = soup.findAll('div',{'action-type':"feed_list_item"})
        if len(root_1) >= 20:
            for r in root_1:
                root_2 = r.find('div', {'class': "content clearfix"})
                mid = r.attrs['mid']
                article_url = root_2.find('div', {'class': "feed_from W_textb"}).findNext('a').attrs['href']
                print article_url
                add_datetime = self.t
                channeltype = 'weibo'
                channel = self.site
                root_content = root_2.find('p', {'class': "comment_txt"})
                long_content = root_content.find('a', {'action-type': "fl_unfold"})
                if long_content:
                    content_url = 'http://s.weibo.com/ajax/direct/morethan140?' + long_content.attrs['action-data']
                    content_html = self.session.get(content_url)
                    content_html = content_html.json()['data']['html']
                    content = BeautifulSoup(content_html, 'html.parser').text.strip().replace("'", "''").replace("%", "\%").replace(":", "\:")
                else:
                    content = root_content.text.strip().replace("'", "''").replace("%", "\%").replace(":", "\:")
                title = content[:30].replace("'", "''").replace("%", "\%").replace(":", "\:")
                author_id = r.attrs['tbinfo']
                author_id = re.findall(r'ouid=(\d+)', author_id)[0]
                author_name = root_2.find('a').attrs['nick-name']
                publish_datetime = root_2.find('a', {'class': "W_textb"}).attrs['date']
                publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(publish_datetime) / 1000))
                root_3 = r.find('div', {'class': "feed_action clearfix"})
                li_list = root_3.findAll('li')

                # 旧版
                # reply_count = r.find('a', {'action-type': "feed_list_comment"}).text
                # reply_count = re.findall(r'\d+', reply_count)
                # if len(reply_count) > 0:
                #     reply_count = int(reply_count[0])
                # else:
                #     reply_count = 0
                # read_count  = 'NULL'
                # like_count = r.find('a', {'action-type': "feed_list_like"}).text
                # like_count = re.findall(r'\d+', like_count)
                # if len(like_count) > 0:
                #     like_count = int(like_count[0])
                # else:
                #     like_count = 0
                # collect_count = r.find('a', {'action-type': "feed_list_favorite"}).text
                # collect_count = re.findall(r'\d+', collect_count)
                # if len(collect_count) > 0:
                #     collect_count = int(collect_count[0])
                # else:
                #     collect_count = 0
                # forward_count = r.find('a', {'action-type': "feed_list_forward"}).text
                # forward_count = re.findall(r'\d+', forward_count)
                # if len(forward_count) > 0:
                #     forward_count = int(forward_count[0])
                # else:
                #     forward_count = 0

                # 新版
                collect_count = li_list[0].find('span').text
                collect_count = re.findall(r'\d+', collect_count)
                if len(collect_count) > 0:
                    collect_count = int(collect_count[0])
                else:
                    collect_count = 0
                forward_count = li_list[1].find('span').text
                forward_count = re.findall(r'\d+', forward_count)
                if len(forward_count) > 0:
                    forward_count = int(forward_count[0])
                else:
                    forward_count = 0
                reply_count = li_list[2].find('span').text
                reply_count = re.findall(r'\d+', reply_count)
                if len(reply_count) > 0:
                    reply_count = int(reply_count[0])
                else:
                    reply_count = 0
                like_count = li_list[0].find('span').text
                like_count = re.findall(r'\d+', like_count)
                if len(like_count) > 0:
                    like_count = int(like_count[0])
                else:
                    like_count = 0
                read_count = 'NULL'
                # print mid, article_url, add_datetime, channeltype, channel, title, content, author_id, author_name, \
                #     publish_datetime, reply_count, read_count, like_count, collect_count, forward_count
                data = [mid, article_url, add_datetime, channeltype, channel, title, content, author_id, author_name,
                        publish_datetime, reply_count, read_count, like_count, collect_count, forward_count]
                if data not in self.result:
                    self.result.append(data)

    def get_url_text(self, query, page):
        html = self.get_index_html(query, page)
        self.get_html_content(html)

    def insert_controller(self):
        for p in range(1, 6):
            # self.get_url_text('中山大学', p)
            # break
            pool.spawn(self.get_url_text, '中山大学', p)
            sleeptime = random.uniform(2, 6)
            gevent.sleep(sleeptime)
        pool.join()
        # self.insert_text()
        self.old_insert_text()

    def insert_text(self):
        valueList = []
        if len(self.result)>0:
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

    def get_update_text(self, url):
        """
        通过url爬取内容
        """
        html = self.session.get(url, cookies=self.load_cookies_from_lwp(self.path_conf + self.filename))  # 加载本地cookies
        # html = self.session.get(url)
        html = html.text
        lindex = html.find('<script>FM.view({"ns":"pl.content.weiboDetail.index"')
        if lindex > 0:
            rindex = html[lindex:].find('</script>')
            rindex = lindex + rindex - 1
            lindex = lindex + len('<script>FM.view(')
            jo = json.loads(html[lindex:rindex])
            data = jo['html']
            # print data
            soup = BeautifulSoup(data, 'lxml')
            root_1  = soup.find('div', {'action-type': "feed_list_item"})
            root_2 = soup.find('div', {'class': "WB_feed_handle"})
            mid = root_1.attrs['mid']
            channel = self.site
            li_list = root_2.findAll('li')
            reply_count = li_list[2]
            reply_count = re.findall(r'\d+', reply_count.text)
            if len(reply_count) > 0:
                reply_count = int(reply_count[0])
            else:
                reply_count = 0
            read_count = 'NULL'
            like_count = li_list[3]
            like_count = re.findall(r'\d+', like_count.text)
            if len(like_count) > 0:
                like_count = int(like_count[0])
            else:
                like_count = 0
            collect_count = li_list[0]
            collect_count = re.findall(r'\d+', collect_count.text)
            if len(collect_count) > 0:
                collect_count = int(collect_count[0])
            else:
                collect_count = 0
            forward_count = li_list[1]
            forward_count = re.findall(r'\d+', forward_count.text)
            if len(forward_count) > 0:
                forward_count = int(forward_count[0])
            else:
                forward_count = 0
            print mid, reply_count, read_count, like_count, collect_count, forward_count
            self.result_update.append([mid, channel, reply_count, read_count, like_count, collect_count, forward_count])

    def update_controller(self):
        sql_query = "SELECT DISTINCT url FROM sa_all_article WHERE channel = '%s'" % self.site
        query = session.execute(sql_query)
        for q in query:
            # print q['url']
            # self.get_update_text( q['url'])
            # break
            pool.spawn(self.get_update_text, q['url'])
            sleeptime = random.uniform(0.1, 1)
            gevent.sleep(sleeptime)
        pool.join()
        # self.update_text()

    def update_text(self):
        valueList = []
        if len(self.result_update)>0:
            for q in self.result_update:
                valueList.append(
                    " ('%s','%s',%s,%s,%s,%s,%s,'%s') " %
                    (q[0], q[1], q[2], q[3], q[4], q[5], q[6], self.t))
            sql = """
                INSERT INTO sa_all_article (mid, channel, reply_count, read_count, like_count, collect_count,
                forward_count, update_datetime) VALUES
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
                    " ('%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,'%s') " %
                    (q[7], q[0], q[6], q[2], q[9], 'null', 'null', q[14], q[10], q[12], q[8]))
            sql = """
                INSERT INTO t_sinablog (userid,mid,content,add_datetime,publish_datetime,publish_method,forward_mid,
                forward_count,comment_count,like_count,username) VALUES
            """
            sql1 = """
                ON DUPLICATE KEY UPDATE
                comment_count = IF(comment_count<VALUES(comment_count), VALUES(comment_count), comment_count),
                like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
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


if __name__ == "__main__":
    print '_______start_______'
    start = time.time()
    # logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
    weibo = WeiBo()
    weibo.login("raiche_qrc@yahoo.com.cn", "623981")
    weibo.insert_controller()
    # weibo.update_controller()
    # weibo.get_update_text('http://weibo.com/6298186905/FkoeL9U6m?refer_flag')
    # weibo.get_update_text('http://weibo.com/1227220061/FjFe3wogc?refer_flag')
    session.close()
    end = time.time()
    print '%.4f' % (end - start)
