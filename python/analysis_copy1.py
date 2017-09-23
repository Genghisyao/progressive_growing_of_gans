# -*- coding:utf-8 -*-
import os
from db_init import *
from crawl import *
import math
import argparse

class Processing():
    """
    筛选对应事件的文章
    """
    def __init__(self, event_id, add_datetime, start_datetime, keywords, non_keywords):
        self.event_id = event_id  #事件id
        self.add_datetime = str(add_datetime)
        self.start_datetime = str(start_datetime)
        self.keywords = keywords  #完整关键词
        self.non_keywords = non_keywords  #完整反关键词
        keys = keywords.split(',')
        k_list = []
        for k in keys:
            if k=='中大' or k=='中山大学':
                    continue
            k_list.append('%' + k + '%')
        self.key_list = k_list

    def newsSelect(self):
        """
        筛选————新闻
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" Ttitle LIKE '%s' OR Tcontent LIKE '%s'" % (k, k))
        sql_query = """SELECT * FROM news_text WHERE (""" + 'OR'.join(sql_t) + ") AND Tpublish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        for n in query:
            Tid = n.id
            event_id = self.event_id
            title = n.Ttitle.replace(':','\:')
            add_datetime = n.add_datetime
            publish_datetime = n.Tpublish_datetime
            author_id = ''
            author_name = n.Tauthor_name
            content = n.Tcontent
            reply_count = n.Treply
            read_count = 0
            like_count = 0
            collect_count = 0
            forward_count = 0
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'news'
            channel = n.site
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,
                        reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel,))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
            ON DUPLICATE KEY UPDATE
            reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
            read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
            like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
            collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
            forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
        """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def luntanSelect(self):
        """
        筛选————论坛
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" Ttitle LIKE '%s' OR Tcontent LIKE '%s'" % (k, k))
        sql_query = """SELECT * FROM luntan_text WHERE (""" + 'OR'.join(sql_t) + ") AND Tpublish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        # q_news = session.query(NewsText).filter(or_(NewsText.Ttitle.like(key), NewsText.Tcontent.like(key))).all()
        for n in query:
            Tid = n.id
            event_id = self.event_id
            title = n.Ttitle
            add_datetime = n.add_datetime
            publish_datetime = n.Tpublish_datetime
            author_id = n.Tauthor_id
            author_name = n.Tauthor_name
            content = n.Tcontent
            reply_count = n.Treply
            read_count = n.Tread
            like_count = 0
            collect_count = 0
            forward_count = 0
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'luntan'
            channel = 'bbs.tianya.cn'
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid, event_id, title, add_datetime, publish_datetime, author_id, author_name, content,
                        reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel,))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
                    ON DUPLICATE KEY UPDATE
                    reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                    read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                    like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                    collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                    forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
                """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def tiebaSelect(self):
        """
        筛选————贴吧
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" Ttitle LIKE '%s' OR Tcontent LIKE '%s'" % (k, k))
        sql_query = """SELECT * FROM tieba_text WHERE (""" + 'OR'.join(sql_t) + ") AND Tpublish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        # q_news = session.query(NewsText).filter(or_(NewsText.Ttitle.like(key), NewsText.Tcontent.like(key))).all()
        for n in query:
            Tid = n.id
            event_id = self.event_id
            title = n.Ttitle
            add_datetime = n.add_datetime
            publish_datetime = n.Tpublish_datetime
            author_id = n.Tauthor_id
            author_name = n.Tauthor_name
            content = n.Tcontent
            reply_count = n.Treply
            read_count = 0
            like_count = 0
            collect_count = 0
            forward_count = 0
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'tieba'
            channel = 'tieba.baidu.com'
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid, event_id, title, add_datetime, publish_datetime, author_id, author_name, content,
                        reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel,))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
                            ON DUPLICATE KEY UPDATE
                            reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                            read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                            like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                            collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                            forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
                        """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def zhihuSelect(self):
        """
        筛选————知乎
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" Ttitle LIKE '%s' OR Tcontent LIKE '%s'" % (k, k))
        sql_query = """SELECT * FROM zhihu_text WHERE (""" + 'OR'.join(sql_t) + ") AND Tpublish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        # q_news = session.query(NewsText).filter(or_(NewsText.Ttitle.like(key), NewsText.Tcontent.like(key))).all()
        for n in query:
            Tid = n.id + ';' + n.mid
            event_id = self.event_id
            title = n.Ttitle
            add_datetime = n.add_datetime
            publish_datetime = n.Tpublish_datetime
            author_id = n.Tauthor_id
            author_name = n.Tauthor_name
            content = n.Tcontent
            reply_count = n.Treply
            read_count = n.Tread
            like_count = n.Tlike
            collect_count = n.Tfans
            forward_count = 0
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'zhihu'
            channel = 'zhihu.com'
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid, event_id, title, add_datetime, publish_datetime, author_id, author_name, content,
                        reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
                            ON DUPLICATE KEY UPDATE
                            reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                            read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                            like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                            collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                            forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
                        """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def weiboSelect(self):
        """
        筛选————微博
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" content LIKE '%s' " % k)
        sql_query = """SELECT * FROM t_sinablog WHERE (""" + 'OR'.join(sql_t) + ") AND publish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        # q_news = session.query(NewsText).filter(or_(NewsText.Ttitle.like(key), NewsText.Tcontent.like(key))).all()
        for n in query:
            Tid = n.mid
            event_id = self.event_id
            title = n.content.strip().decode('utf8')[0:19].encode('utf8').replace("'", "''").replace("%", "\%").replace(":", "\:")
            add_datetime = n.add_datetime
            publish_datetime = n.publish_datetime
            author_id = n.userid
            author_name = n.username
            content = n.content.strip().replace("'", "''").replace("%", "\%").replace(":", "\:")
            reply_count = n.comment_count
            read_count = 0
            like_count = n.like_count
            collect_count = 0
            forward_count = n.forward_count
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'weibo'
            channel = 'weibo.com'
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid, event_id, title, add_datetime, publish_datetime, author_id, author_name, content,
                        reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
                            ON DUPLICATE KEY UPDATE
                            reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                            read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                            like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                            collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                            forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
                        """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def weixinSelect(self):
        """
        筛选————微信
        """
        key = self.key_list
        sql_t = []
        for k in key:
            sql_t.append(" title LIKE '%s' OR content LIKE '%s'" % (k, k))
        sql_query = """SELECT * FROM t_weixin WHERE (""" + 'OR'.join(sql_t) + ") AND publish_datetime > '%s'" % self.start_datetime
        query = session.execute(sql_query)
        sql = []
        # q_news = session.query(NewsText).filter(or_(NewsText.Ttitle.like(key), NewsText.Tcontent.like(key))).all()
        for n in query:
            Tid = n.pid + ';' + n.wid
            event_id = self.event_id
            title = n.title
            add_datetime = n.add_datetime
            publish_datetime = n.publish_datetime
            author_id = ''
            author_name = n.author
            content = n.content
            reply_count = 0
            read_count = n.read_count
            like_count = n.like_count
            collect_count = 0
            forward_count = 0
            if reply_count < 0:
                reply_count = 0
            if read_count < 0:
                read_count = 0
            if like_count < 0:
                like_count = 0
            if collect_count < 0:
                collect_count = 0
            if forward_count < 0:
                forward_count = 0
            channeltype = 'weixin'
            channel = 'wx.qq.com'
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (Tid, event_id, title, add_datetime, publish_datetime, author_id, author_name, content,
                        reply_count, read_count, like_count, collect_count, forward_count, channeltype, channel))
        sql_insert1 = "INSERT INTO text_select_copy (Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_insert2 = """
                            ON DUPLICATE KEY UPDATE
                            reply_count = IF(reply_count<VALUES(reply_count), VALUES(reply_count), reply_count),
                            read_count = IF(read_count<VALUES(read_count), VALUES(read_count), read_count),
                            like_count = IF(like_count<VALUES(like_count), VALUES(like_count), like_count),
                            collect_count = IF(collect_count<VALUES(collect_count), VALUES(collect_count), collect_count),
                            forward_count = IF(forward_count<VALUES(forward_count), VALUES(forward_count), forward_count)
                        """
        sql_size = 500
        if len(sql) > 0:
            index = 0
            while index < len(sql):
                # print index, min(index + sql_size, len(sql)) - 1
                sql_insert = sql_insert1 + ','.join(sql[index: min(index + sql_size, len(sql))]) + sql_insert2
                session.execute(sql_insert)
                session.commit()
                index += sql_size

class SelectManager():
    """
    筛选事件文章控制器
    """
    def eventSelect(self):
        sql_query = "SELECT * FROM event_list"
        querys = session.execute(sql_query)
        eventList = list(querys)
        return eventList

    def do(self):
        eventlist = self.eventSelect()
        for e in eventlist:
            event_id = e[0]  # 事件id
            # if event_id < 5:
            #     continue
            event_name = e[1]  # 事件名
            add_datetime = e[2]  # 事件添加时间
            start_datetime = e[3]  # 事件开始时间
            keywords = e[4]  # 事件关键词
            non_keywords = e[5]  # 事件反关键词
            process = Processing(event_id, add_datetime, start_datetime, keywords, non_keywords)
            process.newsSelect()
            process.tiebaSelect()
            process.luntanSelect()
            process.zhihuSelect()
            process.weixinSelect()
            process.weiboSelect()

class ArticleController():
    """
    文章控制器
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def controller(self):
        self.insertGrowth()
        # self.updateArticleHeat1()

    def insertGrowth(self):
        """
        将text_select文章按每小时更新到text_growth_copy和text_analysis中
        :return:
        """
        sql_query = """
            SELECT Tid,event_id,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel
            FROM text_select_copy
        """
        query = session.execute(sql_query)
        valueList = []
        valueList1 = []
        for q in query:
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (q[0],q[1],self.t,q[2],q[3],q[4],q[5],q[6],q[7],q[8]))
            d = self.calculateArticleHeat(q)
            valueList1.append(" ('%s','%s','%s','%s','%s','%s') " % (d[0],d[1],self.t,d[2],d[3],d[4]))

        sql = "INSERT INTO text_growth_copy (Tid,event_id,crawl_datetime,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql1 = "INSERT INTO text_analysis (Tid,event_id,crawl_datetime,channeltype,channel,heat) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

        if len(valueList1) > 0:
            index = 0
            while index < len(valueList1):
                # print index, min(index + sql_size, len(valueList1)) - 1
                sql_insert1 = sql1 + ','.join(valueList1[index: min(index + sql_size, len(valueList1))])
                session.execute(sql_insert1)
                session.commit()
                index += sql_size

    def calculateArticleHeat(self, lis):
        """
        计算文章热度
        :param resultList:
        :return:
        """
        r = lis
        channeltype = r[7]
        if channeltype == 'news':
            reply_count = r[2] * 0.235
            read_count = r[3] * 0.0
            like_count = r[4] * 0.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.0
        if channeltype == 'luntan':
            reply_count = r[2] * 0.030
            read_count = r[3] * 0.085
            like_count = r[4] * 0.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.0
        if channeltype == 'tieba':
            reply_count = r[2] * 0.045
            read_count = r[3] * 0.0
            like_count = r[4] * 0.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.0
        if channeltype == 'zhihu':
            reply_count = r[2] * 0.085
            read_count = r[3] * 0.120
            like_count = r[4] * 0.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.0
        if channeltype == 'weibo':
            reply_count = r[2] * 0.080
            read_count = r[3] * 0.0
            like_count = r[4] * 0.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.120
        if channeltype == 'weixin':
            reply_count = r[2] * 0.0
            read_count = r[3] * 0.150
            like_count = r[4] * 0.060
            collect_count = r[5] * 0.0
            forward_count = r[6] * 0.0
        heat = reply_count + read_count + like_count + collect_count + forward_count
        return [r[0], r[1], r[7], r[8], heat]

    def updateArticleHeat1(self):
        sql1 = "select * from text_growth_copy"  # 更新所有
        query1 = session.execute(sql1)
        result = []
        for r in query1:
            channeltype = r[8]
            channel = r[9]
            if channeltype == 'news':
                reply_count = r[3] * 0.235
                read_count = r[4] * 0.0
                like_count = r[5] * 0.0
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.0
            if channeltype == 'luntan':
                reply_count = r[3] * 0.030
                read_count = r[4] * 0.085
                like_count = r[5] * 0.0
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.0
            if channeltype == 'tieba':
                reply_count = r[3] * 0.045
                read_count = r[4] * 0.0
                like_count = r[5] * 0.0
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.0
            if channeltype == 'zhihu':
                reply_count = r[3] * 0.085
                read_count = r[4] * 0.120
                like_count = r[5] * 0.0
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.0
            if channeltype == 'weibo':
                reply_count = r[3] * 0.080
                read_count = r[4] * 0.0
                like_count = r[5] * 0.0
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.120
            if channeltype == 'weixin':
                reply_count = r[3] * 0.0
                read_count = r[4] * 0.150
                like_count = r[5] * 0.060
                collect_count = r[6] * 0.0
                forward_count = r[7] * 0.0
            heat = reply_count + read_count + like_count + collect_count + forward_count
            result.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], heat])

        # 更新text_growth热度值
        valueList = []
        sql2 = "INSERT INTO text_analysis VALUES "
        sql3 = " ON DUPLICATE KEY UPDATE heat=VALUES(heat)"
        for d in result:
            valueList.append(" ('%s','%s','%s','%s','%s','%s') " % (
            d[0], d[1], d[2], d[8], d[9], d[10]))
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                sql_insert = sql2 + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql3
                # print sql_insert
                session.execute(sql_insert)
                session.commit()
                index += sql_size

class ArticleController1():
    """
    文章控制器
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def controller(self):
        # self.insertGrowth()
        self.updateHeat()
        # self.updateAllHeat()

    def insertGrowth(self):
        """
        将text_select文章按每小时更新到text_growth_copy和text_analysis中
        :return:
        """
        sql_query = """
            SELECT Tid,event_id,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel
            FROM text_select_copy
        """
        query = session.execute(sql_query)
        valueList = []
        valueList1 = []
        for q in query:
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (q[0],q[1],self.t,q[2],q[3],q[4],q[5],q[6],q[7],q[8]))
            d = self.calculateArticleHeat(q)

        sql = "INSERT INTO text_growth_copy (Tid,event_id,crawl_datetime,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def updateHeat(self):
        sql_query = """
            SELECT a.Tid,a.event_id,a.reply_count,a.read_count,a.like_count,a.collect_count,a.forward_count,a.channeltype,a.channel,b.publish_datetime,a.crawl_datetime
            FROM text_growth_copy a
            LEFT JOIN text_select_copy b
            ON a.Tid=b.Tid AND a.channel = b.channel
            WHERE a.crawl_datetime = (SELECT MAX(crawl_datetime) FROM text_growth_copy)
        """
        query = session.execute(sql_query)
        valueList1 = []
        for q in query:
            d = self.calculateArticleHeat(q)
            valueList1.append(" ('%s','%s','%s','%s','%s','%s') " % (d[0],d[1],q['crawl_datetime'],d[2],d[3],d[4]))

        sql1 = " INSERT INTO text_analysis_copy (Tid,event_id,crawl_datetime,channeltype,channel,heat) VALUES "
        sql2 = " ON DUPLICATE KEY UPDATE heat=VALUES(heat) "
        sql_size = 500
        if len(valueList1) > 0:
            index = 0
            while index < len(valueList1):
                # print index, min(index + sql_size, len(valueList1)) - 1
                sql_insert1 = sql1 + ','.join(valueList1[index: min(index + sql_size, len(valueList1))]) + sql2
                session.execute(sql_insert1)
                session.commit()
                index += sql_size

    def updateAllHeat(self):
        sql_query = """
            SELECT a.Tid,a.event_id,a.reply_count,a.read_count,a.like_count,a.collect_count,a.forward_count,a.channeltype,a.channel,b.publish_datetime,a.crawl_datetime
            FROM text_growth_copy a
            LEFT JOIN text_select_copy b
            ON a.Tid=b.Tid AND a.channel = b.channel
        """
        query = session.execute(sql_query)
        valueList1 = []
        for q in query:
            d = self.calculateArticleHeat(q)
            valueList1.append(" ('%s','%s','%s','%s','%s','%s') " % (d[0],d[1],q['crawl_datetime'],d[2],d[3],d[4]))
        sql1 = " INSERT INTO text_analysis_copy (Tid,event_id,crawl_datetime,channeltype,channel,heat) VALUES "
        sql2 = " ON DUPLICATE KEY UPDATE heat=VALUES(heat) "
        sql_size = 500
        if len(valueList1) > 0:
            index = 0
            while index < len(valueList1):
                # print index, min(index + sql_size, len(valueList1)) - 1
                sql_insert1 = sql1 + ','.join(valueList1[index: min(index + sql_size, len(valueList1))]) + sql2
                session.execute(sql_insert1)
                session.commit()
                index += sql_size

    def calculateArticleHeat(self, lis):
        """
        计算文章热度
        :param resultList:
        :return:
        """
        r = lis
        channeltype = r[7]
        publish_datetime = time.mktime(r[9].timetuple())
        if channeltype == 'news':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        if channeltype == 'luntan':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        if channeltype == 'tieba':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        if channeltype == 'zhihu':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        if channeltype == 'weibo':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        if channeltype == 'weixin':
            reply_count = r[2] * 0.8
            read_count = r[3] * 0.0
            like_count = r[4] * 3.0
            collect_count = r[5] * 0.0
            forward_count = r[6] * 1.0
        ts = publish_datetime -time.time()
        if reply_count + like_count + forward_count != 0.0:
            heat = math.log10(reply_count + like_count + forward_count) + ts / 45000
        else:
            heat = ts / 45000
        return [r[0], r[1], r[7], r[8], heat]

class MediaController():
    """
    媒体控制器
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def controller(self):
        self.all_insertStatistics()
        # self.all_updateMediaHeat()
        self.only_insertMediaHeat()
        # self.only_updateMediaHeat()

    def all_insertStatistics(self):
        event_id = 0
        sql_query = """
            SELECT SUM(reply_count), SUM(read_count), SUM(like_count), SUM(collect_count), COUNT(*), SUM(forward_count), channeltype, channel
            FROM text_select_copy
            GROUP BY channeltype, channel
        """
        query = session.execute(sql_query)
        valueList = []
        for q in query:
            d = self.all_calculateMediaHeat(q)
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (event_id,self.t,d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]))
        sql = "INSERT INTO media_statistics (event_id,crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total,channeltype,channel,media_heat) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def all_calculateMediaHeat(self, lis):
        """
        计算媒体热度
        :param resultList:
        :return:
        """
        r = lis
        channeltype = r[6]
        if channeltype == 'news':
            reply_count = float(r[0]) * 0.235
            read_count = float(r[1]) * 0.0
            like_count = float(r[2]) * 0.0
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.0
        if channeltype == 'luntan':
            reply_count = float(r[0]) * 0.030
            read_count = float(r[1]) * 0.085
            like_count = float(r[2]) * 0.0
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.0
        if channeltype == 'tieba':
            reply_count = float(r[0]) * 0.045
            read_count = float(r[1]) * 0.0
            like_count = float(r[2]) * 0.0
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.0
        if channeltype == 'zhihu':
            reply_count = float(r[0]) * 0.085
            read_count = float(r[1]) * 0.120
            like_count = float(r[2]) * 0.0
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.0
        if channeltype == 'weibo':
            reply_count = float(r[0]) * 0.080
            read_count = float(r[1]) * 0.0
            like_count = float(r[2]) * 0.0
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.120
        if channeltype == 'weixin':
            reply_count = float(r[0]) * 0.0
            read_count = float(r[1]) * 0.150
            like_count = float(r[2]) * 0.060
            collect_count = float(r[3]) * 0.0
            original_count = float(r[4]) * 0.0
            forward_count = float(r[5]) * 0.0
        heat = reply_count + read_count + like_count + collect_count + original_count +forward_count
        return [r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], heat]

    def all_updateMediaHeat(self):
        """
        从text_select_copy获取主键，在media_statistics找到相关主键的历史记录，取4条记录进行热度计算
        :return:
        """
        event_id = 0
        sql1 = "SELECT channeltype, channel FROM text_select_copy GROUP BY channeltype, channel"
        query1 = session.execute(sql1)
        for q1 in query1:
            sql2  = "select * from media_statistics WHERE channeltype = '%s' AND channel = '%s' AND event_id = %d ORDER BY crawl_datetime DESC" % (q1[0], q1[1], event_id)
            query2 = session.execute(sql2)
            lis = []
            for q2 in query2:
                lis.append(list(q2))
            data = self.all_calculateMediaHeat(lis)


            # 更新media_statistics热度值
            valueList = []
            sql3 = "INSERT INTO media_statistics VALUES "
            for d in data:
                valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10]))
            sql_size = 500
            if len(valueList) > 0:
                index = 0
                while index < len(valueList):
                    sql_insert = sql3 + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + " ON DUPLICATE KEY UPDATE media_heat=VALUES(media_heat)"
                    # print sql_insert
                    session.execute(sql_insert)
                    session.commit()
                    index += sql_size

    def only_insertMediaHeat(self):
        sql_query = """
            SELECT event_id, SUM(reply_count), SUM(read_count), SUM(like_count), SUM(collect_count), COUNT(*), SUM(forward_count), channeltype, channel
            FROM text_select_copy
            GROUP BY event_id, channeltype, channel
        """
        query = session.execute(sql_query)
        valueList = []
        for q in query:
            d = self.only_calculateMediaHeat(q)
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (d[0], self.t, q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], d[9]))
        sql = "INSERT INTO media_statistics (event_id,crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total,channeltype,channel,media_heat) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def only_calculateMediaHeat(self, lis):
        """
        计算媒体热度
        :param resultList:
        :return:
        """
        r = lis
        channeltype = r[7]
        if channeltype == 'news':
            reply_count = float(r[1]) * 0.235
            read_count = float(r[2]) * 0.0
            like_count = float(r[3]) * 0.0
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.0
        if channeltype == 'luntan':
            reply_count = float(r[1]) * 0.030
            read_count = float(r[2]) * 0.085
            like_count = float(r[3]) * 0.0
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.0
        if channeltype == 'tieba':
            reply_count = float(r[1]) * 0.045
            read_count = float(r[2]) * 0.0
            like_count = float(r[3]) * 0.0
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.0
        if channeltype == 'zhihu':
            reply_count = float(r[1]) * 0.085
            read_count = float(r[2]) * 0.120
            like_count = float(r[3]) * 0.0
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.0
        if channeltype == 'weibo':
            reply_count = float(r[1]) * 0.080
            read_count = float(r[2]) * 0.0
            like_count = float(r[3]) * 0.0
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.120
        if channeltype == 'weixin':
            reply_count = float(r[1]) * 0.0
            read_count = float(r[2]) * 0.150
            like_count = float(r[3]) * 0.060
            collect_count = float(r[4]) * 0.0
            original_count = float(r[5]) * 0.0
            forward_count = float(r[6]) * 0.0
        heat = reply_count + read_count + like_count + collect_count + original_count +forward_count
        return [r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], heat]

    def only_updateMediaHeat(self):
        sql1 = "SELECT * FROM media_statistics"
        query1 = session.execute(sql1)
        lis = []
        for q1 in query1:
            lis.append(list(q1))
        data = self.only_calculateMediaHeat(lis)
        # 更新event_statistics热度值
        valueList = []
        sql2 = "INSERT INTO media_statistics VALUES "
        sql3 = " ON DUPLICATE KEY UPDATE media_heat=VALUES(media_heat)"
        for d in data:
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " % (d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9],d[10]))
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                sql_insert = sql2 + ','.join(valueList[index: min(index + sql_size, len(valueList))]) + sql3
                session.execute(sql_insert)
                session.commit()
                index += sql_size

class EventController():
    """
    事件控制器
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def controller(self):
        # self.insertStatistics()
        self.updateEventHeat()

    def insertStatistics(self):
        sql_query = """
            SELECT event_id, SUM(reply_count), SUM(read_count), SUM(like_count), SUM(collect_count), COUNT(*), SUM(forward_count)
            FROM text_select_copy
            GROUP BY event_id
        """
        query = session.execute(sql_query)
        valueList = []
        for q in query:
            valueList.append(" ('%s','%s','%s','%s','%s','%s','%s','%s') " % (q[0],self.t,q[1],q[2],q[3],q[4],q[5],q[6]))
        sql = "INSERT INTO event_statistics_copy (event_id,crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

    def updateEventHeat(self):
        """
        根据media_statistics的热度计算事件热度
        :return:
        """
        sql1 = """
            INSERT INTO event_statistics_copy
            SELECT event_id, crawl_datetime, SUM(reply_total), SUM(read_total), SUM(like_total), SUM(collect_total), SUM(original_total), SUM(forward_total), SUM(media_heat)
            FROM media_statistics
            GROUP BY event_id, crawl_datetime
            ON DUPLICATE KEY UPDATE event_heat = VALUES(event_heat)
        """
        session.execute(sql1)
        session.commit()

class Warning():
    """
    预警模块
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = time.strftime('%Y%m%d', time.localtime(time.time()))

    def allWarning(self):
        sql_warning = "SELECT * FROM warning_value WHERE event_id = 0"
        warningList = session.execute(sql_warning)
        dataList = []
        for w in warningList:
            # 统计量&热度&来源预警
            sql_query1 = "SELECT * FROM (SELECT * FROM event_statistics_copy ORDER BY crawl_datetime DESC) a WHERE a.event_id>0 GROUP BY event_id"
            query1 = session.execute(sql_query1)
            for q1 in query1:
                # 评论预警
                if q1['reply_total'] > w['threshold_reply']:
                    event_id = q1['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'reply'
                    threshold_value = w['threshold_reply']
                    if level == 1:
                        reason = u'评论红色预警'
                    elif level == 2:
                        reason = u'评论橙色预警'
                    elif level == 3:
                        reason = u'评论黄色预警'
                    elif level == 4:
                        reason = u'评论蓝色预警'
                    else:
                        reason = ''
                    data_value = q1['reply_total']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id,level,warning_datetime,type,threshold_value,reason,data_value

                # 阅读预警
                if q1['read_total'] > w['threshold_read']:
                    event_id = q1['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'read'
                    threshold_value = w['threshold_read']
                    if level == 1:
                        reason = u'阅读红色预警'
                    elif level == 2:
                        reason = u'阅读橙色预警'
                    elif level == 3:
                        reason = u'阅读黄色预警'
                    elif level == 4:
                        reason = u'阅读蓝色预警'
                    else:
                        reason = ''
                    data_value = q1['read_total']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id,level,warning_datetime,type,threshold_value,reason,data_value

                # 转发预警
                if q1['forward_total'] > w['threshold_forward']:
                    event_id = q1['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'forward'
                    threshold_value = w['threshold_forward']
                    if level == 1:
                        reason = u'转发红色预警'
                    elif level == 2:
                        reason = u'转发橙色预警'
                    elif level == 3:
                        reason = u'转发黄色预警'
                    elif level == 4:
                        reason = u'转发蓝色预警'
                    else:
                        reason = ''
                    data_value = q1['forward_total']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id,level,warning_datetime,type,threshold_value,reason,data_value

                # 热度预警
                if q1['event_heat'] > w['threshold_heat']:
                    event_id = q1['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'heat'
                    threshold_value = w['threshold_heat']
                    if level == 1:
                        reason = u'热度红色预警'
                    elif level == 2:
                        reason = u'热度橙色预警'
                    elif level == 3:
                        reason = u'热度黄色预警'
                    elif level == 4:
                        reason = u'热度蓝色预警'
                    else:
                        reason = ''
                    data_value = q1['event_heat']
                    data = [event_id,level,warning_datetime,type,threshold_value,reason,data_value]
                    dataList.append(data)
                    # print event_id,level,warning_datetime,type,threshold_value,reason,data_value

                # 总来源预警
                if q1['original_total'] > w['threshold_original']:
                    event_id = q1['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'original'
                    threshold_value = w['threshold_original']
                    if level == 1:
                        reason = u'总来源红色预警'
                    elif level == 2:
                        reason = u'总来源橙色预警'
                    elif level == 3:
                        reason = u'总来源黄色预警'
                    elif level == 4:
                        reason = u'总来源蓝色预警'
                    else:
                        reason = ''
                    data_value = q1['original_total']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id, level, warning_datetime, type, threshold_value, reason, data_value

            # 媒体预警
            sql_query2 = "SELECT event_id, chi FROM text_select_copy LEFT JOIN translation ON channeltype=eng GROUP BY event_id, channeltype"
            query2 = session.execute(sql_query2)
            for q2 in query2:
                if q2['chi'] in w['threshold_channel']:
                    event_id = q2['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'media'
                    threshold_value = w['threshold_channel']
                    if level == 1:
                        reason = u'媒体红色预警'
                    elif level == 2:
                        reason = u'媒体橙色预警'
                    elif level == 3:
                        reason = u'媒体黄色预警'
                    elif level == 4:
                        reason = u'媒体蓝色预警'
                    else:
                        reason = ''
                    data_value = q2['chi']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id, level, warning_datetime, type, threshold_value, reason, data_value

            # 省份预警
            sql_query3 = """
                SELECT t1.event_id, COUNT(region) AS region FROM
                (SELECT a.event_id, substring_index(substring_index(a.ip_address,';',2),';',-1) AS region
                FROM text_select_comment a
                LEFT JOIN text_select_copy b
                ON b.Tid = a.source_url
                WHERE a.ip_address LIKE '中国%' AND a.ip_address <> ''
                GROUP BY a.event_id, region) t1
                GROUP BY t1.event_id
            """
            query3 = session.execute(sql_query3)
            for q3 in query3:
                if q3['region'] > w['threshold_province']:
                    event_id = q3['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'province'
                    threshold_value = w['threshold_province']
                    if level == 1:
                        reason = u'省份数红色预警'
                    elif level == 2:
                        reason = u'省份数橙色预警'
                    elif level == 3:
                        reason = u'省份数黄色预警'
                    elif level == 4:
                        reason = u'省份数蓝色预警'
                    else:
                        reason = ''
                    data_value = q3['region']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id, level, warning_datetime, type, threshold_value, reason, data_value

            # 国家预警
            sql_query4 = """
                SELECT t1.event_id, COUNT(country) AS country FROM
                (SELECT a.event_id, substring_index(ip_address,';',1) AS country
                FROM text_select_comment a
                LEFT JOIN text_select_copy b
                ON Tid = source_url
                WHERE ip_address NOT LIKE '中国%' AND ip_address <> ''
                GROUP BY event_id, country) t1
                GROUP BY t1.event_id
            """
            query4 = session.execute(sql_query4)
            for q4 in query4:
                if q4['country'] > w['threshold_foreign']:
                    # print q2
                    event_id = q4['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'country'
                    threshold_value = w['threshold_foreign']
                    if level == 1:
                        reason = u'国家数红色预警'
                    elif level == 2:
                        reason = u'国家数橙色预警'
                    elif level == 3:
                        reason = u'国家数黄色预警'
                    elif level == 4:
                        reason = u'国家数蓝色预警'
                    else:
                        reason = ''
                    data_value = q4['country']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id, level, warning_datetime, type, threshold_value, reason, data_value

            # 网民数预警
            sql_query5 = """
                SELECT a.event_id, COUNT(*) AS netizen_number
                FROM text_select_comment a
                LEFT JOIN text_select b
                ON Tid = source_url
                WHERE a.ip_address <> ''
                GROUP BY a.event_id
            """
            query5 = session.execute(sql_query5)
            for q5 in query5:
                if q5['netizen_number'] > w['threshold_netizen']:
                    event_id = q5['event_id']
                    level = w['level']
                    warning_datetime = self.t
                    type = 'netizen_number'
                    threshold_value = w['threshold_netizen']
                    if level == 1:
                        reason = u'网民总数红色预警'
                    elif level == 2:
                        reason = u'网民总数橙色预警'
                    elif level == 3:
                        reason = u'网民总数黄色预警'
                    elif level == 4:
                        reason = u'网民总数蓝色预警'
                    else:
                        reason = ''
                    data_value = q5['netizen_number']
                    data = [event_id, level, warning_datetime, type, threshold_value, reason, data_value]
                    dataList.append(data)
                    # print event_id, level, warning_datetime, type, threshold_value, reason, data_value

        dataList.sort()
        warningValues = []
        warningStatus = []
        for d in dataList:
            warningValues.append(" ('%s','%s','%s','%s','%s','%s','%s') " % (d[0],d[1],d[2],d[3],d[4],d[5],d[6]))
            warningStatus.append(" ('%s','%s','%s','%s') " % (d[0], d[1], d[3], 0))
            # print d[0],d[1],d[2],d[3],d[4],d[5],d[6]

        sql_insert  = " INSERT INTO warning_list VALUES " + ','.join(warningValues)
        sql_insert += " ON DUPLICATE KEY UPDATE data_value = VALUES(data_value)"
        session.execute(sql_insert)
        session.commit()

        sql_insert_status = " INSERT IGNORE INTO warning_status VALUES " + ','.join(warningStatus)
        session.execute(sql_insert_status)
        session.commit()

class HeatWords():
    """
    关键词模块
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.d = time.strftime('%Y%m%d', time.localtime(time.time()))
        self.root_path = os.path.dirname(os.getcwd())  # 根目录
        self.conf_path = self.root_path + r'\conf'  # image目录

    def insertHeatWords(self):
        path = self.conf_path + '\stopword.txt'
        f = open(path)
        text = f.read().decode("gbk")
        stopWords = text.split(',')
        # stopWords = ['...', 'via', 'video', u'中山大学', u'中大', u'视频', u'校园', u'学校', u'高校', u'大学', u'学生', u'师生', u'广州',
        #              u'深圳', u'如何', u'评价', u'链接', u'网页', u'原标题']
        # 各个事件关键词
        sql_query1 = " SELECT event_id FROM event_list "
        query1 = session.execute(sql_query1)
        sql = []
        for q in query1:
            sql_query2 = " SELECT title FROM text_select_copy WHERE event_id=%d " % q.event_id
            query2 = session.execute(sql_query2)
            longcontent = '\n'.join(map(lambda x: x[0], query2))  # 将所有文章标题连接
            for w in stopWords:
                longcontent = longcontent.replace(w, '')
            # 分析关键词
            import jieba.analyse
            tags = jieba.analyse.extract_tags(longcontent, topK=15, withWeight=True)
            for t in tags:
                # print q.event_id,t[0],t[1]
                sql.append(" ('%s','%s','%s','%s') "% (q.event_id, self.t ,t[0] ,t[1]))
                # print q.event_id, self.t, t[0], t[1]

        # 所有事件关键词
        sql_query3 = " SELECT title FROM text_select_copy "
        query3 = session.execute(sql_query3)
        longcontent = '\n'.join(map(lambda x: x[0], query3))
        for w in stopWords:
            longcontent = longcontent.replace(w, '')
        alls = jieba.analyse.extract_tags(longcontent, topK=20, withWeight=True)
        for a in alls:
            # print a[0], a[1]
            sql.append(" ('%s','%s','%s','%s') " % (0, self.t, a[0], a[1]))
        sql_insert = " INSERT INTO event_heatwords VALUES " + ','.join(sql)
        session.execute(sql_insert)
        session.commit()
        # print ','.join(sql)


if __name__ == '__main__':
    print "——————————start——————————"
    start = time.time()

    parser = argparse.ArgumentParser(description='analysis module')
    parser.add_argument('--selectArticle', dest='selectArticle',
                        action='store_true', help='文章筛选', default=False)
    parser.add_argument('--updateArticle', dest='updateArticle',
                        action='store_true', help='文章热度更新', default=False)
    parser.add_argument('--updateArticle1', dest='updateArticle1',
                        action='store_true', help='文章热度更新1', default=False)
    parser.add_argument('--updateAllArticle1', dest='updateAllArticle1',
                        action='store_true', help='所有文章热度更新1', default=False)
    parser.add_argument('--updateMedia', dest='updateMedia',
                        action='store_true', help='媒体指标更新', default=False)
    parser.add_argument('--updateEvent', dest='updateEvent',
                        action='store_true', help='事件指标更新', default=False)
    args = parser.parse_args()

    if args.selectArticle:
        SelectManager().do()
    if args.updateArticle:
        ArticleController().controller()
    if args.updateArticle1:
        ArticleController1().controller()
    if args.updateAllArticle1:
        ArticleController1().updateAllHeat()
    if args.updateMedia:
        MediaController().controller()
    if args.updateMedia:
        HeatWords().insertHeatWords()

    # SelectManager().do()
    # ArticleController().controller()
    # ArticleController1().controller()
    # ArticleController1().updateAllHeat()
    # MediaController().controller()
    # EventController().controller()
    # Warning().allWarning()
    # HeatWords().insertHeatWords()
    session.close()
    end = time.time()
    print '%.4f' % (end - start)