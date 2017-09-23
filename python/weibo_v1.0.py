# -*- coding:utf-8 -*-
import os
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
        """
        constructor
        """
        self.user_name = None
        self.pass_word = None
        self.user_uniqueid = None
        self.user_nick = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"})
        self.session.get("http://weibo.com/login.php")
        self.result_list = []
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
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



    def get_index_html(self, query, page):
        query = urllib.quote(query)
        params = {
            'scope': 'ori',  # 类型
            'suball': '1',  # 包含全部
            'timescope': 'custom:2017-01-01:',  # 时间
            'Refer': 'g',
            'page': page
        }
        index_url = 'http://s.weibo.com/weibo/'+ query  # 搜索主页+查询词
        html = self.session.get(index_url, params=params).text
        lindex = html.find('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct"')
        rindex = html[lindex:].find('</script>')
        rindex = lindex + rindex - 1
        lindex = lindex + len('<script>STK && STK.pageletM && STK.pageletM.view(')
        jo = json.loads(html[lindex:rindex])
        data = jo['html']  # 实时微博页面
        # print type(data)
        # print data
        return data


    def get_html_content(self, data):
        soup = BeautifulSoup(data, 'html.parser')
        root_1 = soup.findAll('div',{'action-type':"feed_list_item"})
        for r in root_1:
            mid = r.attrs['mid']
            root_2 = r.find('div', {'class':"content clearfix"})
            author_id = root_2.find('a').attrs['usercard']
            author_id = re.findall(r'id=(\d+)&', author_id)[0]
            author_name = root_2.find('a').attrs['nick-name']
            root_content = root_2.find('p', {'class':"comment_txt"})
            long_content = root_content.find('a', {'action-type': "fl_unfold"})
            if long_content:
                content_url = 'http://s.weibo.com/ajax/direct/morethan140?' + long_content.attrs['action-data']
                content_html = self.session.get(content_url)
                content_html = content_html.json()['data']['html']
                content = BeautifulSoup(content_html, 'html.parser').text.strip().replace(' ', '').replace(":", "\:")
            else:
                content = root_content.text.strip().replace(' ', '')
            title = content[:30]
            add_datetime = self.t
            publish_datetime = root_2.find('a',{'class':"W_textb"}).attrs['date']
            publish_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(publish_datetime)/1000))
            collect_count = r.find('a', {'action-type':"feed_list_favorite"}).find('span').text
            collect_count = re.findall(r'\d+', collect_count)
            if len(collect_count)>0:
                collect_count = int(collect_count[0])
            else:
                collect_count = 0

            forward_count = r.find('a', {'action-type': "feed_list_forward"}).find('span').text
            forward_count = re.findall(r'\d+', forward_count)
            if len(forward_count) > 0:
                forward_count = int(forward_count[0])
            else:
                forward_count = 0

            reply_count = r.find('a', {'action-type': "feed_list_comment"}).find('span').text
            reply_count = re.findall(r'\d+', reply_count)
            if len(reply_count) > 0:
                reply_count = int(reply_count[0])
            else:
                reply_count = 0

            like_count = r.find('a', {'action-type': "feed_list_like"}).find('span').text
            like_count = re.findall(r'\d+', like_count)
            if len(like_count) > 0:
                like_count = int(like_count[0])
            else:
                like_count = 0
            self.result_list.append([mid,add_datetime,publish_datetime,author_id,author_name,title,content,reply_count,like_count,collect_count,forward_count])
            # print mid, author_id, author_name, publish_datetime
            # print title
            # print collect_count, forward_count, reply_count, like_count
            # # print content
            # print '*' * 50

    def insert_data(self):
        if self.result_list:
            # print len(self.result_list)
            valueList = []
            for q in self.result_list:
                valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10]))
            sql = "INSERT INTO weibo_text (mid,add_datetime,publish_datetime,author_id,author_name,title,content,reply_count,like_count,collect_count,forward_count) VALUES "
            sql1 = "ON DUPLICATE KEY UPDATE reply_count=VALUES(reply_count),like_count=VALUES(reply_count),collect_count=VALUES(reply_count),forward_count=VALUES(reply_count)"
            sql_size = 500
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql1
                session.execute(sql_insert)
                session.commit()
                index += sql_size


    def controller(self, query, page):
        html = self.get_index_html(query, page)
        self.get_html_content(html)


if __name__ == "__main__":
    print '_______start_______'
    start = time.time()
    # logging.basicConfig(level=logging.DEBUG, format="%(asctime)s\t%(levelname)s\t%(message)s")
    weibo = WeiBo()
    weibo.login("raiche_qrc@yahoo.com.cn", "623981")
    # for p in range(1, 10):
        # print '第%d页'% p
        # # weibo.controller('中山大学', p)
        # pool.spawn(weibo.controller, '中山大学', p)
        # gevent.sleep(2)
    # pool.join()
    # weibo.insert_data()
    # weibo.get_exception_code()
    session.close()
    end = time.time()
    print '%.4f' % (end - start)
