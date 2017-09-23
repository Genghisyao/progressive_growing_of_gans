# -*- coding:utf-8 -*-
from db_init import *
import time
import datetime


class HotArticle():

    def __init__(self):
        self.result = list()
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = datetime.date.today()

    def get_hot_article_zhihu(self, deltaday):
        before_date = datetime.date.today() - datetime.timedelta(days=deltaday)
        sql1 = """
        SELECT mid, Ttitle, add_datetime, Tpublish_datetime, Tauthor_id, Tauthor_name, Tcontent, Treply, Tread, Tlike
        FROM zhihu_text WHERE Tpublish_datetime>'%s' AND Tread>5000
        """% (before_date)
        query1 = session.execute(sql1)
        for q1 in query1:
            Tid = q1['mid']
            title = q1['Ttitle']
            add_datetime = q1['add_datetime']
            publish_datetime = q1['Tpublish_datetime']
            author_id = q1['Tauthor_id']
            author_name = q1['Tauthor_name']
            content = q1['Tcontent'].replace("'", "''").replace("%", "\%").replace(":", "\:")
            reply_count = q1['Treply']
            read_count = q1['Tread']
            like_count = 'NULL'
            collect_count = 'NULL'
            forward_count = 'NULL'
            channeltype = 'luntan'
            channel = 'zhihu.com'
            heat = reply_count * 0.085 + read_count * 0.120
            self.result.append(
                [Tid, title, add_datetime, publish_datetime, author_id, author_name, content, reply_count, read_count,
                 like_count, collect_count, forward_count, channeltype, channel, heat])

    def get_hot_article_weibo(self, deltaday):
        before_date = datetime.date.today() - datetime.timedelta(days=deltaday)
        sql1 = """
        SELECT mid, content, add_datetime, publish_datetime, userid, username, comment_count, like_count, forward_count
        FROM t_sinablog WHERE publish_datetime>'%s' AND (forward_count>20 OR comment_count>20)
        """% (before_date)
        query1 = session.execute(sql1)
        for q1 in query1:
            Tid = q1['mid']
            title = q1['content'][:30]
            add_datetime = q1['add_datetime']
            publish_datetime = q1['publish_datetime']
            author_id = q1['userid']
            author_name = q1['username']
            content = q1['content'].replace("'", "''").replace("%", "\%").replace(":", "\:")
            reply_count = q1['comment_count']
            read_count = 'NULL'
            like_count = q1['like_count']
            collect_count = 'NULL'
            forward_count = q1['forward_count']
            channeltype = 'weibo'
            channel = 'weibo.com'
            heat = reply_count * 0.080 + forward_count * 0.120
            self.result.append(
                [Tid, title, add_datetime, publish_datetime, author_id, author_name, content, reply_count, read_count,
                 like_count, collect_count, forward_count, channeltype, channel, heat])

    def insert_controller(self):
        self.get_hot_article_zhihu(7)
        self.get_hot_article_weibo(7)
        self.insert_text()

    def insert_text(self):
        valueList = []
        if len(self.result) > 0:
            for q in self.result:
                valueList.append(
                    " ('%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,'%s','%s',%s) " %
                    (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11], q[12], q[13], q[14]))
            sql = """
                INSERT INTO hot_article (Tid, title, add_datetime, publish_datetime, author_id, author_name,
                content, reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel,
                heat) VALUES
            """
            sql1 = """
                ON DUPLICATE KEY UPDATE
                reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count),
                heat = VALUES(heat)
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
    print 'start'
    start = time.time()
    # print datetime.date.today() - datetime.timedelta(days=7)
    # HotArticle().get_hot_article_zhihu(7)
    # HotArticle().get_hot_article_weibo(7)
    HotArticle().insert_controller()

    session.close()
    end = time.time()
    print '%.4f' % (end - start)
