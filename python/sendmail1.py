# -*- coding:utf-8 -*-
import smtplib
import time
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase

class sendWarning():
    """
    发送预警
    """
    def __init__(self):
        import smtplib
        import time
        from email.header import Header
        from email.utils import parseaddr, formataddr
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = time.strftime('%Y%m%d', time.localtime(time.time()))

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr(( \
            Header(name, 'utf-8').encode(), \
            addr.encode('utf-8') if isinstance(addr, unicode) else addr))

    def sendMail(self, to_addr, subject, content, html=False, imagepath=None):
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

        # 添加附件
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
        # if imagepath:
            # image = MIMEApplication(open(imagepath, 'rb').read())
            # image.add_header('Content-Disposition', 'attachment', filename=imagepath)
            # msg.attach(image)

        # server = smtplib.SMTP(smtp_server, smtp_port)  # 非ssl
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # ssl
        server.set_debuglevel(0)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()

if __name__ == '__main__':
    print 'start#####'
    sendWarning().sendMail("627818082@qq.com", u'舆情预警通知', u'中文测试', 'captcha.jpg')