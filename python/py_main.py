# -*- coding:utf-8 -*-
import argparse
from db_init import *
from crawl import *
from analysis import *
from gevent import monkey, pool
import gevent
monkey.patch_all()
pool = pool.Pool(10)
str_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

class TX_manager():
    """
    数据库插入————腾讯
    """

    def text(self, query, starttime, endtime):
        site = 'news.qq.com'
        baidu = Baidu_crawl(query, site, starttime, endtime)
        TXnews = TXnews_crawl()
        urls = baidu.getUrl()  #获取百度搜索结果urls
        if len(urls) > 0:
            [pool.spawn(TXnews.getText, url) for url in urls]
            pool.join()

    def comment(self):
        TXnews = TXnews_crawl()
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'news.qq.com' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(TXnews.getComment, q.Tid, q.event_id)
                time.sleep(0.1)
            # [pool.spawn(TXnews.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class WY_manager():
    """
    数据库插入————网易163
    """

    def text(self, query, starttime, endtime):
        site = 'news.163.com'
        baidu = Baidu_crawl(query, site, starttime, endtime)
        WYnews = WYnews_crawl()
        urls = baidu.getUrl()  #获取百度搜索结果urls
        if urls:
            [pool.spawn(WYnews.getText, url) for url in urls]
            pool.join()

    def comment(self):
        WYnews = WYnews_crawl()
        # query = session.query(NewsText).filter(NewsText.site == 'news.163.com').all()
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'news.163.com' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(WYnews.getComment, q.Tid, q.event_id)
                time.sleep(0.1)
            #     WYnews.getComment(q.Tid, q.event_id)
            # [pool.spawn(WYnews.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class XL_manager():
    """
    数据库插入————新浪sina
    """

    def text(self, query, starttime, endtime):
        site = 'news.sina.com.cn'
        baidu = Baidu_crawl(query, site, starttime, endtime)
        XLnews = XLnews_crawl()
        urls = baidu.getUrl()  #获取百度搜索结果urls
        if urls:
            [pool.spawn(XLnews.getText, url) for url in urls]
            pool.join()

    def comment(self):
        XLnews = XLnews_crawl()
        # query = session.query(NewsText).filter(NewsText.site == 'news.sina.com.cn').all()
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'news.sina.com.cn' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(XLnews.getComment, q.Tid, q.event_id)
                time.sleep(0.1)
            # [pool.spawn(XLnews.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class FH_manager():
    """
    数据库插入————凤凰ifeng
    """

    def text(self, query, starttime, endtime):
        site = 'news.ifeng.com'
        baidu = Baidu_crawl(query, site, starttime, endtime)
        FHnews = FHnews_crawl()
        urls = baidu.getUrl()  #获取百度搜索结果urls
        if urls:
            [pool.spawn(FHnews.getText, url) for url in urls]
            pool.join()

    def comment(self):
        FHnews = FHnews_crawl()
        # query = session.query(NewsText).filter(NewsText.site == 'news.ifeng.com').all()
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'news.ifeng.com' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(FHnews.getComment, q.Tid, q.event_id)
                time.sleep(0.1)
            # [pool.spawn(FHnews.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class People_manager():
    """
    数据库插入————人民网
    """

    def text(self, query, starttime, endtime):
        site = 'people.com.cn'
        baidu = Baidu_crawl(query, site, starttime, endtime)
        PeopleNews = PeopleNews_crawl()
        urls = baidu.getUrl()  #获取百度搜索结果urls
        if urls:
            [pool.spawn(PeopleNews.getText, url) for url in urls]
            pool.join()

    def comment(self):
        PeopleNews = PeopleNews_crawl()
        # query = session.query(NewsText).filter(NewsText.site == 'people.com.cn').all()
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'people.com.cn' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(PeopleNews.getComment, q.Tid, q.event_id)
                time.sleep(0.1)
            # [pool.spawn(PeopleNews.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class News_insert():
    """
    数据库插入————新闻正文和评论
    """

    def text(self):
        sql = []
        while not newsText_queue.empty():
            result = newsText_queue.get()
            if result:
                result[2] = result[2].replace("'", "''").replace("%", "\%").replace(":", "\:")
                result[6] = result[6].replace("'", "''").replace("%", "\%").replace(":", "\:")
                # session.merge(NewsText(id=result[0], site=result[1], Ttitle=result[2], add_datetime=str_datetime, Tpublish_datetime=result[3], Tauthor_name=result[4], Treply=result[5], Tcontent=result[6]))
                sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s') " %
                           (result[0], result[1], result[2], str_datetime, result[3], result[4], result[5], result[6]))
        if sql:
            insert_sql = "INSERT INTO news_text (id,site,Ttitle,add_datetime,Tpublish_datetime,Tauthor_name,Treply,Tcontent) VALUES"
            insert_sql = insert_sql + ','.join(sql)
            insert_sql = insert_sql + "ON DUPLICATE KEY UPDATE Treply=VALUES(Treply)"
            session.execute(insert_sql)
            session.commit()

class luntan_manager():
    """
    数据库插入————天涯论坛
    """
    def __init__(self, query, page):
        self.query = query  # 查询关键字
        self.page = page  # 页数

    def text(self):
        luntan = luntan_crawl(self.query)
        [pool.spawn(luntan.getUrl, page) for page in range(1, self.page + 1)]
        pool.join()
        while not luntanUrl_queue.empty():
            url = luntanUrl_queue.get()
            pool.spawn(luntan.getText, url)
        pool.join()
        sql = []
        while not luntanText_queue.empty():
            i = luntanText_queue.get()
            i[1] = i[1].replace("'", "''").replace("%", "\%").replace(":", "\:")
            i[7] = i[7].replace("'", "''").replace("%", "\%").replace(":", "\:")
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (i[0], i[1], str_datetime, i[2], i[3], i[4], i[5], i[6], i[7]))
        if sql:
            insert_sql = "INSERT INTO luntan_text (id,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tread,Treply,Tcontent) VALUES"
            insert_sql = insert_sql + ','.join(sql)
            insert_sql = insert_sql + "ON DUPLICATE KEY UPDATE Tread=VALUES(Tread), Treply=VALUES(Treply)"
            session.execute(insert_sql)
            session.commit()

    def comment(self):
        luntan = luntan_crawl(self.query)
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'bbs.tianya.cn' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            [pool.spawn(luntan.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class tieba_manager():
    """
    数据库插入————百度贴吧
    """
    def __init__(self, query, page):
        self.query = query  # 查询关键字
        self.page = page

    def text(self):
        tieba = tieba_crawl(self.query)
        [pool.spawn(tieba.getUrl, page) for page in range(1, self.page + 1)]
        pool.join()
        while not tiebaUrl_queue.empty():
            url = tiebaUrl_queue.get()
            pool.spawn(tieba.getText, url)
        pool.join()
        sql = []
        while not tiebaText_queue.empty():
            i = tiebaText_queue.get()
            i[1] = i[1].replace("'", "''").replace("%", "\%").replace(":", "\:")
            i[6] = i[6].replace("'", "''").replace("%", "\%").replace(":", "\:")
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (i[0], i[1], str_datetime, i[2], i[3], i[4], i[5], i[6]))
        if sql:
            insert_sql = "INSERT INTO tieba_text (id,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Treply,Tcontent) VALUES"
            insert_sql = insert_sql + ','.join(sql)
            insert_sql = insert_sql + "ON DUPLICATE KEY UPDATE Treply=VALUES(Treply)"
            session.execute(insert_sql)
            session.commit()

    def comment(self):
        tieba = tieba_crawl(self.query)
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'tieba.baidu.com' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            [pool.spawn(tieba.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class ZH_manager():
    """
    数据库插入————知乎
    """
    def __init__(self, query, page):
        self.query = query  # 查询关键字
        self.page = page

    def text(self):
        zhihu = zhihu_crawl(self.query)
        pool.map(zhihu.getUrl, range(1, self.page + 1))
        pool.join()
        while not zhihuUrl_queue.empty():
            url = zhihuUrl_queue.get_nowait()
            # zhihu.getText(url)
            pool.spawn(zhihu.getText, url)
            # pool.spawn(zhihu.getText2, url)
            time.sleep(1)
        pool.join
        sql = []
        while not zhihuText_queue.empty():
            i = zhihuText_queue.get_nowait()
            i[10] = i[10].replace("'", "''").replace("%", "\%").replace(":", "\:")
            sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                       (i[0], i[1], i[2], str_datetime, i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10]))
        if sql:
            insert_sql = "INSERT INTO zhihu_text (id,mid,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tfans,Tread,Treply,Tlike,Tcontent) VALUES"
            insert_sql = insert_sql + ','.join(sql)
            insert_sql = insert_sql + "ON duplicate KEY UPDATE Tfans=VALUES(Tfans),Tread=VALUES(Tread),Treply=VALUES(Treply),Tlike=VALUES(Tlike)"
            session.execute(insert_sql)
            session.commit()
        #     try:
        #         insert_sql = """
        #             INSERT INTO zhihu_text (id,mid,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tfans,Tread,Treply,Tlike,Tcontent)
        #             VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
        #             ON duplicate KEY UPDATE Tfans=VALUES(Tfans),Tread=VALUES(Tread),Treply=VALUES(Treply),Tlike=VALUES(Tlike)
        #         """ % (i[0],i[1],i[2],str_datetime,i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10])
        #         session.execute(insert_sql)
        #         session.commit()
        #     except Exception, e:
        #         print 'Insert error:', e
        #         break
    def comment(self):
        zhihu = zhihu_crawl(self.query)
        query_sql = " SELECT DISTINCT Tid, event_id FROM text_select WHERE channel = 'zhihu.com' AND reply_count>0 "
        query = session.execute(query_sql)
        if query:
            for q in query:
                pool.spawn(zhihu.getComment, q.Tid, q.event_id)
                time.sleep(0.5)
            # [pool.spawn(zhihu.getComment, q.Tid, q.event_id) for q in query]
            pool.join()

class Comment_insert():
    """
    数据库插入————评论
    """

    def comment(self):
        sql = []
        while not allComm_queue.empty():
            i = allComm_queue.get()
            if i:
                i[14] = i[14].replace("'", "''").replace("%", "\%").replace(":", "\:")
                sql.append(" ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') " %
                           (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14],i[15],i[16],i[17]))
        if sql:
            insert_sql = "INSERT INTO text_select_comment VALUES"
            insert_sql = insert_sql + ','.join(sql)
            insert_sql = insert_sql + "ON DUPLICATE KEY UPDATE like_count=VALUES(like_count),unlike_count=VALUES(unlike_count),read_count=VALUES(read_count),reply_count=VALUES(reply_count)"
            session.execute(insert_sql)
            session.commit()

class SelectManager():

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

if __name__ == '__main__':
    CrawlDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    
    parser = argparse.ArgumentParser(description='public opinion')
    parser.add_argument('--dropdb', dest='dropdb',
                        action='store_true', help='清空数据库', default=False)
    parser.add_argument('--init', dest='init',
                        action='store_true', help='初始化所有', default=False)
    parser.add_argument('--newsText', dest='newsText',
                        action='store_true', help='新闻正文爬取', default=False)
    parser.add_argument('--newsComm', dest='newsComm',
                        action='store_true', help='新闻评论爬取', default=False)
    parser.add_argument('--tiebaText', dest='tiebaText',
                        action='store_true', help='贴吧正文爬取', default=False)
    parser.add_argument('--tiebaComm', dest='tiebaComm',
                        action='store_true', help='贴吧评论爬取', default=False)
    parser.add_argument('--luntanText', dest='luntanText',
                        action='store_true', help='论坛正文爬取', default=False)
    parser.add_argument('--luntanComm', dest='luntanComm',
                        action='store_true', help='论坛评论爬取', default=False)
    parser.add_argument('--zhihuText', dest='zhihuText',
                        action='store_true', help='知乎正文爬取', default=False)
    parser.add_argument('--zhihuComm', dest='zhihuComm',
                        action='store_true', help='知乎评论爬取', default=False)
    parser.add_argument('--select', dest='select',
                        action='store_true', help='正文关键字提取', default=False)
    parser.add_argument('--growth', dest='growth',
                        action='store_true', help='评读转赞增长', default=False)
    parser.add_argument('--indication', dest='indication',
                        action='store_true', help='统计分析', default=False)
    args = parser.parse_args()

    if args.init:
        None
    elif args.dropdb:
        None
    else:
        if args.newsText:
            TX_manager().text('中山大学', '2017-01-01', CrawlDate)
            News_insert().text()
            WY_manager().text('中山大学', '2017-01-01', CrawlDate)
            News_insert().text()
            XL_manager().text('中山大学', '2017-01-01', CrawlDate)
            News_insert().text()
            FH_manager().text('中山大学', '2017-01-01', CrawlDate)
            News_insert().text()
            People_manager().text('中山大学', '2017-01-01', CrawlDate)
            News_insert().text()
        if args.newsComm:
            TX_manager().comment()
            Comment_insert().comment()
            WY_manager().comment()
            Comment_insert().comment()
            XL_manager().comment()
            Comment_insert().comment()
            FH_manager().comment()
            Comment_insert().comment()
            People_manager().comment()
            Comment_insert().comment()
        if args.tiebaText:
            tieba_manager('中山大学', 15).text()
        if args.tiebaComm:
            tieba_manager('中山大学', 15).comment()
            Comment_insert().comment()
        if args.luntanText:
            luntan_manager('中山大学', 15).text()
        if args.luntanComm:
            luntan_manager('中山大学', 15).comment()
            Comment_insert().comment()
        if args.zhihuText:
            ZH_manager('中山大学', 15).text()
        if args.zhihuComm:
            ZH_manager('中山大学', 15).comment()
            Comment_insert().comment()
        if args.select:
            SelectManager().do()
        if args.growth:
            Growth().updateGrowth()
            Growth().updateArticleHeat()
        if args.indication:
            Indication().insertEventHeat()
            Indication().updateEventHeat()
            Indication().insertHeatWords()

    start = time.time()
    # print Baidu_crawl('中山大学', 'news.qq.com', '2017-01-01', '2017-07-01').getUrl()
    # TX_manager().text('中山大学', '2017-01-01', CrawlDate)
    # News_insert().text()
    # WY_manager().text('中山大学', 'news.163.com', '2017-01-01', CrawlDate)
    # News_insert().text()
    # XL_manager().text('中山大学', 'news.sina.com.cn', '2017-01-01', CrawlDate)
    # News_insert().text()
    # FH_manager().text('中山大学', 'news.ifeng.com', '2017-01-01', CrawlDate)
    # News_insert().text()
    # People_manager().text('中山大学', 'people.com.cn', '2017-01-01', CrawlDate)
    # News_insert().text()

    # luntan_manager('中山大学', 10).text()
    # tieba_manager('中山大学', 10).text()
    # ZH_manager('中山大学', 10).text()

    # TX_manager().comment()
    # Comment_insert().comment()
    # WY_manager().comment()
    # Comment_insert().comment()
    # XL_manager().comment()
    # Comment_insert().comment()
    # FH_manager().comment()
    # Comment_insert().comment()
    # People_manager().comment()
    # Comment_insert().comment()
    # luntan_manager('中山大学', 15).comment()
    # Comment_insert().comment()
    # tieba_manager('中山大学', 15).comment()
    # Comment_insert().comment()
    # ZH_manager('中山大学', 15).comment()
    # Comment_insert().comment()
    # query_sql = """SELECT * FROM text_select_comment WHERE user_ip  <> '' """
    # query = session.execute(query_sql)
    # for q in query:
    #     # print q.user_ip, q.ip_address
    #     pool.spawn(get_ip_address().get, q.user_ip)
    #     time.sleep(0.1)
        # get_ip_address().get(q.user_ip)

    # SelectManager().do()
    # Growth().updateGrowth()
    # Growth().updateArticleHeat()
    # Indication().insertEventHeat()
    # Indication().updateEventHeat()
    # Indication().insertHeatWords()



    end = time.time()
    print end-start
    session.close()