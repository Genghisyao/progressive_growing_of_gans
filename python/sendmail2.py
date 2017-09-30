# -*- coding:utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from db_init import *
import smtplib
import time
import json
# send(signal_type, title, content)

class sendWarning():
    """
    发送预警
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = time.strftime('%Y%m%d', time.localtime(time.time()))


    def controller(self,signal_type,title,contents):
        send_query = "SELECT * FROM (SELECT * FROM warning_send ORDER BY add_datetime DESC) a GROUP BY warning_type"
        status_query = "SELECT * FROM warning_status WHERE status = 0"
        sendResult = session.execute(send_query)
        statusResult = session.execute(status_query)
        statusResult = map(lambda x: x[:], statusResult)
        if statusResult:
            for q in sendResult:
                # print q ,'111'
                add_datetime = q[0]
                warning_type = q[1]
                # condition = json.loads(q[2])
                method = json.loads(q[3])
                #设置敏感词为keyword
                if signal_type == 'sensitive_words':
                    signal_type = 'keyword'
                if(warning_type == signal_type):

                    # resultList = self.lineMessage(contents)
                        # for r in resultList:
                        #     print r[0],r[1],r[2],r[3],r[4],r[5],r[6]
                    content = self.htmlContent(contents)
                    for m in method:
                        if m['type'] == 'email':
                            to_addr = ','.join(m['value'])
                                # print to_addr
                            self.sendMail(to_addr, title, content, html=True)
                            print u'邮件已发送'

                        if m['type'] == 'message':
                            phone_number = ','.join(m['value'])
                            print u'短信未开通'

                        if m['type'] == 'wechat':
                            print u'微信公众号未开通'

            # sql_insert = "INSERT INTO warning_status (SELECT * FROM warning_status WHERE status = 0) ON DUPLICATE KEY UPDATE status = 1"
            # session.execute(sql_insert)
            # session.commit()

    # def lineMessage(self, condition):
    #     resultList = []
    #     for i in condition:
    #         if i['type'] == 'heat':
    #             type = u'热度'
    #             sql_heat = """
    #                                 SELECT b.warning_datetime, c.event_name, chi, b.threshold_value, b.data_value, b.reason
    #                                 FROM warning_status a
    #                                 LEFT JOIN warning_list b
    #                                 ON a.event_id = b.event_id AND a.`level` = b.`level` AND a.type = b.type
    #                                 LEFT JOIN event_list c
    #                                 ON a.event_id = c.event_id
    #                                 LEFT JOIN translation
    #                                 ON a.type = eng
    #                                 WHERE a.`status` = 0 AND a.`level` <= '%s' AND a.`type` = '%s'
    #                                 GROUP BY a.event_id, a.`type`
    #                             """ % (i['value'], i['type'])
    #             query_heat = session.execute(sql_heat)
    #             for j in query_heat:
    #                 resultList.append([type, str(j.warning_datetime), j.event_name, j.chi, str(j.threshold_value),
    #                                    str(j.data_value), j.reason])
    #
    #         if i['type'] == 'media':
    #             type = u'媒体'
    #             sql_media = """
    #                                 SELECT b.warning_datetime, c.event_name, chi, b.threshold_value, b.data_value, b.reason
    #                                 FROM warning_status a
    #                                 LEFT JOIN warning_list b
    #                                 ON a.event_id = b.event_id AND a.`level` = b.`level` AND a.type = b.type
    #                                 LEFT JOIN event_list c
    #                                 ON a.event_id = c.event_id
    #                                 LEFT JOIN translation
    #                                 ON a.type = eng
    #                                 WHERE a.`status` = 0 AND a.`level` <= '%s' AND (a.`type` = '%s' OR a.`type` = '%s')
    #                                 GROUP BY a.event_id, a.`type`
    #                             """ % (i['value'], 'media', 'original')
    #             query_media = session.execute(sql_media)
    #             for j in query_media:
    #                 resultList.append([type, str(j.warning_datetime), j.event_name, j.chi, j.threshold_value,
    #                                    j.data_value, j.reason])
    #
    #         if i['type'] == 'area':
    #             type = u'地域'
    #             sql_area = """
    #                                 SELECT b.warning_datetime, c.event_name, chi, b.threshold_value, b.data_value, b.reason
    #                                 FROM warning_status a
    #                                 LEFT JOIN warning_list b
    #                                 ON a.event_id = b.event_id AND a.`level` = b.`level` AND a.type = b.type
    #                                 LEFT JOIN event_list c
    #                                 ON a.event_id = c.event_id
    #                                 LEFT JOIN translation
    #                                 ON a.type = eng
    #                                 WHERE a.`status` = 0 AND a.`level` <= '%s' AND (a.`type` = '%s' OR a.`type` = '%s')
    #                                 GROUP BY a.event_id, a.`type`
    #                             """ % (i['value'], 'province', 'netizen_number')
    #             query_area = session.execute(sql_area)
    #             for j in query_area:
    #                 resultList.append([type, str(j.warning_datetime), j.event_name, j.chi, str(j.threshold_value),
    #                                    str(j.data_value), j.reason])
    #     return resultList

    def htmlContent(self, resultList):
        trList = []
        for r in resultList:
            #print type(r[0]), type(r[1]), type(r[2]), type(r[3]), type(r[4]), type(r[5]), type(r[6])

            content = u"""
                <tr>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                    <td style="border:1px solid #000;padding:5px 10px;">%s</td>
                </tr>
            """% (r[0],r[1],r[2],r[3],r[4],r[5],r[6])
            trList.append(content)
        html  = u"""
            <html>
            <head>
                <title></title>
            </head>
            <body>
            <table style="border-collapse:collapse;">
                <thead>
                    <tr>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">预警类型</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">预警时间</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">文章标题</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">指标类型</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">阈值</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">现值</th>
                        <th style="font-weight: 700;border:1px solid #000;padding:5px 10px;">原因</th>
                    </tr>
                </thead>
                <tbody>
                    %s
                </tbody>
            </table>
            </body>
            </html>
        """% ''.join(trList)
        return html

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
        from_addr = '1048418294@qq.com'  # 发送人邮箱
        password = 'yxfxlvzliisybdjd' # 发送人邮箱密码 'jbaldhvlukyzbfje'
        smtp_server = 'smtp.qq.com'  # 邮箱服务器
        smtp_port = 465  # 邮箱端口号
        to_addr = '1106066690@qq.com'
        print to_addr
        if html:
            msg = MIMEText(content, 'html', 'utf-8')  # 发html邮件
        else:
            msg = MIMEText(content, 'plain', 'utf-8')  # 发纯文本邮件
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = self._format_addr(u'发送人 <%s>' % from_addr)
        msg['To'] = self._format_addr(u'收件人 <%s>' % to_addr)
        # server = smtplib.SMTP(smtp_server, smtp_port)  # 非ssl
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # ssl
        server.set_debuglevel(0)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()

if __name__ == '__main__':
    print "——————————start——————————"
    start = time.time()
    # sendWarning().getWarningMessage()
    arr =[ ['1','2','3','4','5','6','7']]
    print len(arr)
    sendWarning().controller('sensitive_words','预警',arr)
    session.close()
    end = time.time()
    print '%.4f' % (end-start)