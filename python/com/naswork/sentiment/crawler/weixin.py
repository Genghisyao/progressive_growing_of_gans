'''
Created on 11 Apr 2017

@author: eyaomai
'''
import csv
import codecs
import os
import sys
sys.path.append(sys.argv[0][:sys.argv[0].rfind(os.path.join('com','naswork'))])
from urllib import quote
from bs4 import BeautifulSoup
from com.naswork.sentiment.crawler.sessioncrawler import SessionCrawler
from com.naswork.sentiment.common.utils import MySqlProxy, Logging, Configuration
import json
import time
import datetime

APP_NAME = 'weixin'
ISOTIMEFORMAT      = '%Y-%m-%d %H:%M:%S'
SOUGO_QUERY_URL = 'http://weixin.sogou.com/weixin?type=%d&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_='
AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
SOUGO_HEADER = {
    'User-Agent': AGENT,
    'Host': "weixin.sogou.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en,zh;q=0.8,zh-CN;q=0.6",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests":"1"
}
WX_HEADER = {
    'User-Agent': AGENT,
    'Host': "mp.weixin.qq.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en,zh;q=0.8,zh-CN;q=0.6",
    "Connection": "keep-alive",
    "Cache-Control":"max-age=0",
    "Upgrade-Insecure-Requests":"1"
}
WX_COMMENT_HEADER = {
    'User-Agent': AGENT,
    'Host': "mp.weixin.qq.com",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en,zh;q=0.8,zh-CN;q=0.6",
    "Connection": "keep-alive",
    "X-Requested-With":"XMLHttpRequest"
}
WX_ARTICLE_LIST_PREFIX = 'var msgList = '
WX_ARTICLE_LIST_SUFFIX = 'seajs.use'
WX_COMMENT_URL = 'http://mp.weixin.qq.com/mp/getcomment?src=3&ver=1&timestamp=%d&%s&&uin=&key=&pass_ticket=&wxtoken=&devicetype=&clientversion=0&x5=0&f=json'

class WeiXinCrawlerByTopic(object):
    def __init__(self, sleepRange, logger):
        '''
        Constructor
        '''
        self.logger = logger
        self.session = SessionCrawler(None, sleepRange, self.logger)

    def __querySogou(self, sougoUrl):
        '''
        Given the official account id, we expect to uniquely find one and only one item
        Return the url to the official account
        '''
        self.logger.debug('Query sougo %s', sougoUrl)
        content = self.session.get(sougoUrl, SOUGO_HEADER)
        soup = BeautifulSoup(content)
        ul = soup.findAll('ul',{'class':'news-list'})[0]
        liList = ul.findAll('li')
        for li in liList:
            aList = li.findAll('a')
            articleUrl = None
            for a in aList:
                if a['uigs'].startswith('article_title'):
                    articleUrl = a['href']
                    break
            if articleUrl is not None:
                header = WX_HEADER.copy()
                header['Referer'] = sougoUrl
                self.session.randomSleep()
                content = self.session.get(articleUrl, header)
                article = self.parseArticle(content)
                article.contentUrl = articleUrl
                queryComment(self.session, articleUrl, article)

    def parseArticle(self, content):
        soup = BeautifulSoup(content)
        article = Article()
        #content
        div = soup.findAll('div',{'class':'rich_media_content'})
        if len(div)==0:
            #it may be due to that this post has been banned
            self.logger.warn('No content')
            return None
            #raise Exception('No content for %s'% article.title)
        article.content = div[0].text

        #title in <title> ... </title>
        title = soup.findNext('title')
        
        article.title = title.text
        article.wid = hash(article.title)
        
        #find meta list
        divMeta = soup.findAll('div',{'class':'rich_media_meta_list'})[0]
        
        #post date
        emPostdate = divMeta.findAll('em',{'id':'post-date'})[0]
        article.publishDateTime = time.mktime(datetime.datetime.strptime(emPostdate.text, '%Y-%m-%d').timetuple())
        
        #author
        emAuthorList = divMeta.findAll('em',{'class':'rich_media_meta rich_media_meta_text'})
        for em in emAuthorList:
            if 'id' not in em.attrs:
                article.author = em.text
                break
        
        #profile
        divProfile = divMeta.findAll('div',{'class':'profile_inner'})[0]
        ##nickname
        strong = divProfile.findAll('strong',{'class':'profile_nickname'})[0]
        article.userName = strong.text
        ##userid
        article.userId = strong.findNext('span').text
        
        return article

def queryComment(session, referer, article):
    #find the signature
    lindex= article.contentUrl.find('signature=')
    rindex = article.contentUrl[lindex:].find('&')
    if rindex>0:
        signature = article.contentUrl[lindex:rindex]
    else:
        signature = article.contentUrl[lindex:]
    #find the timestamp
    lindex= article.contentUrl.find('timestamp=')+len('timestamp=')
    timestamp = int(article.contentUrl[lindex:lindex+10])
    
    #query
    url = WX_COMMENT_URL % (timestamp, signature)
    header = WX_COMMENT_HEADER.copy()
    header['Referer'] = referer
    session.randomSleep()
    content = session.get(url, header)
    jo = json.loads(content)

    article.readCount = jo['read_num']
    article.likeCount = jo['like_num']
    commentList = jo['comment']
    for item in commentList:
        comment = Comment()
        comment.commenterNickName = item['nick_name']
        comment.likeCount = item['like_num']
        comment.content = item['content']
        comment.contentId = item['content_id']
        comment.createTime = item['create_time']
        for replyItem in item['reply']['reply_list']:
            reply = Reply()
            reply.content = replyItem['content']
            reply.createTime = replyItem['create_time']
            reply.uin = replyItem['uin']
            reply.toUin = replyItem['to_uin']
            reply.replyId = replyItem['reply_id']
            comment.replyList.append(reply)
        article.commentList.append(comment)
    
class WeiXinCralwer(object):
    '''
    classdocs
    '''


    def __init__(self, sleepRange, logger):
        '''
        Constructor
        '''
        self.logger = logger
        self.session = SessionCrawler(None, sleepRange, self.logger)

    def __querySogou(self, sougoUrl):
        '''
        Given the official account id, we expect to uniquely find one and only one item
        Return the url to the official account
        '''
        self.logger.debug('Query sougo %s', sougoUrl)
        content = self.session.get(sougoUrl, SOUGO_HEADER)
        soup = BeautifulSoup(content)
        item = soup.findAll('a',{'uigs':'account_name_0'})[0]
        return item['href']

    def __queryArticleList(self, sougoUrl, officialAccountUrl):
        self.logger.debug('Query ariticle list for %s', officialAccountUrl)
        header = WX_HEADER.copy()
        header['Referer'] = sougoUrl
        self.session.randomSleep()
        content = self.session.get(officialAccountUrl, header)
        lindex = content.find(WX_ARTICLE_LIST_PREFIX)+len(WX_ARTICLE_LIST_PREFIX)
        rindex = content.find(WX_ARTICLE_LIST_SUFFIX)
        rindex = lindex + content[lindex:rindex].rfind(';')
        js = content[lindex:rindex]
        jo = json.loads(js)
        aList = jo['list']
        articleList = list()
        for item in aList:
            app_msg_ext_info = item['app_msg_ext_info']
            comm_msg_info = item['comm_msg_info']            
            article = self.__fetchArticle(app_msg_ext_info)
            article.publishDateTime = comm_msg_info['datetime']
            articleList.append(article)
            if 'multi_app_msg_item_list' in item:
                for embedItem in item['multi_app_msg_item_list']:
                    article = self.__fetchArticle(embedItem)
                    article.publishDateTime = comm_msg_info['datetime']
                    articleList.append(article)
        return articleList
    
    def __fetchArticle(self, item):
        article = Article()
        article.title = item['title']
        article.wid = str(hash(article.title))
        article.author = item['author']
        article.contentUrl = item['content_url']
        article.digest = item['digest']
        article.fileid = item['fileid']
        article.sourceUrl = item['source_url']
        #print article.title,":",article.contentUrl,'\n'
        return article
    
    def __queryComment(self, articleList, referer):
        mainPageHeader = WX_HEADER.copy()
        mainPageHeader['Referer'] = referer
        for article in articleList:
            self.logger.debug('Query comment for %s', article.title)
            #find the signature
            lindex= article.contentUrl.find('signature=')
            rindex = article.contentUrl[lindex:].find('&')
            if rindex>0:
                signature = article.contentUrl[lindex:rindex]
            else:
                signature = article.contentUrl[lindex:]
            #find the timestamp
            lindex= article.contentUrl.find('timestamp=')+len('timestamp=')
            timestamp = int(article.contentUrl[lindex:lindex+10])
            self.session.randomSleep()
            #query main page
            mainUrl = 'http://mp.weixin.qq.com'+article.contentUrl.replace('&amp;','&')
            self.session.randomSleep()
            content = self.session.get(mainUrl, mainPageHeader)
            soup = BeautifulSoup(content)
            div = soup.findAll('div',{'class':'rich_media_content'})
            if len(div)==0:
                #it may be due to that this post has been banned
                self.logger.warn('No content for %s', article.title)
                continue
                #raise Exception('No content for %s'% article.title)
            article.content = div[0].text
            #query comment page
            currentTime = int(time.time())
            url = WX_COMMENT_URL % (timestamp, signature)
            #print url
            header = WX_COMMENT_HEADER.copy()
            header['Referer'] = mainUrl
            self.session.randomSleep()
            content = self.session.get(url, header)
            jo = json.loads(content)
            #print jo.keys()
            article.readCount = jo['read_num']
            article.likeCount = jo['like_num']
            commentList = jo['comment']
            for item in commentList:
                comment = Comment()
                comment.commenterNickName = item['nick_name']
                comment.likeCount = item['like_num']
                comment.content = item['content']
                comment.contentId = item['content_id']
                comment.createTime = item['create_time']
                for replyItem in item['reply']['reply_list']:
                    reply = Reply()
                    reply.content = replyItem['content']
                    reply.createTime = replyItem['create_time']
                    reply.uin = replyItem['uin']
                    reply.toUin = replyItem['to_uin']
                    reply.replyId = replyItem['reply_id']
                    comment.replyList.append(reply)
                article.commentList.append(comment)

    def crawl(self, officialAccountId):
        
        sougoUrl = SOUGO_QUERY_URL % (1, quote(officialAccountId))
        officialAccountUrl = self.__querySogou(sougoUrl)
        articleList = self.__queryArticleList(sougoUrl, officialAccountUrl)
        self.__queryComment(articleList, officialAccountUrl)
        return articleList
        #self.__writeCsv(officialAccountId+'.csv', articleList)

    def writeDb(self, dbConf, officialAccountId, articleList):
        dbProxy = MySqlProxy(host=dbConf['dbHost'], 
                             port=3306, user=dbConf['dbUser'], 
                             passwd=dbConf['dbPasswd'], db=dbConf['dbName'])
        weixinSql = 'INSERT INTO T_WEIXIN (pid, wid, author, title, digest, content, publish_datetime, read_count, like_count) values '
        commentSql = 'INSERT INTO T_WEIXIN_COMMENT(pid, cid, wid, content, publisher_name, publish_datetime,like_count) values '
        replySql = 'INSERT INTO T_WEIXIN_REPLY (rid, cid, content, publish_datetime, uin, touin) values '
        weixinValueList = list()
        commentValueList = list()
        replyValueList = list()
        widSet = set()
        for article in articleList:
            weixinValueList.append('("%s","%s","%s","%s","%s","%s","%s",%d,%d)'%(
                                    officialAccountId,
                                    str(article.wid),
                                    article.author.replace('"','\\"'),
                                    article.title.replace('"','\\"'),
                                    article.digest.replace('"','\\"'),
                                    article.content.replace('"','\\"'),
                                    time.strftime(ISOTIMEFORMAT, time.localtime(article.publishDateTime)),
                                    article.readCount,
                                    article.likeCount
                                        ))
            widSet.add(article.fileid)
            for comment in article.commentList:
                commentValueList.append('("%s","%s","%s","%s","%s","%s",%d)'%(
                                            officialAccountId,
                                            str(comment.contentId),
                                            str(article.wid),
                                            comment.content.replace('"','\\"'),
                                            comment.commenterNickName.replace('"','\\"'),
                                            time.strftime(ISOTIMEFORMAT, time.localtime(comment.createTime)),
                                            comment.likeCount
                                        ))
                for reply in comment.replyList:
                    replyValueList.append('("%s","%s","%s","%s","%s","%s")'%(
                                            str(reply.replyId),
                                            str(comment.contentId),
                                            reply.content.replace('"','\\"'),
                                            time.strftime(ISOTIMEFORMAT, time.localtime(reply.createTime)),
                                            reply.uin,
                                            reply.toUin
                                        ))

        #clear the db firstly
        sql = 'delete from T_WEIXIN where wid in (%s) and pid="%s"' % (','.join(map(lambda x: '"'+str(x)+'"', widSet)), officialAccountId)
        dbProxy.execute(sql)
        sql = 'delete from T_WEIXIN_REPLY where cid in (select cid from T_WEIXIN_COMMENT where wid in (%s) and pid="%s")' % (','.join(map(lambda x: '"'+str(x)+'"', widSet)), officialAccountId)
        dbProxy.execute(sql)
        sql = 'delete from T_WEIXIN_COMMENT where wid in (%s) and pid="%s"' % (','.join(map(lambda x: '"'+str(x)+'"', widSet)), officialAccountId)
        dbProxy.execute(sql)

        #insert to db
        if len(weixinValueList)>0:
            self.logger.info('Insert %d records to weixin', len(weixinValueList))
            dbProxy.execute(weixinSql +','.join(weixinValueList))
        if len(commentValueList)>0:
            self.logger.info('Insert %d records to comment', len(commentValueList))
            dbProxy.execute(commentSql +','.join(commentValueList))
        if len(replyValueList)>0:
            self.logger.info('Insert %d records to reply', len(replyValueList))
            dbProxy.execute(replySql +','.join(replyValueList))
        
    def __writeCsv(self, fileName, articleList):
        #f = codecs.open(fileName,"w","utf-8")
        csvfile = file(fileName,'w')
        csvfile.write(codecs.BOM_UTF8)
        writer = csv.writer(csvfile)
        header = ['Title', 'Digest', 'Author', 'readCount', 'likeCount', 'publishDateTime', 'Comment-NickName', 'Comment-Content', 'Comment-likeCount', 'Comment-CreateTime']
        writer.writerow(header)
        for article in articleList:
            writer.writerow(
                            (
                              article.title.encode('utf8'),
                              article.digest.encode('utf8'),
                              article.author.encode('utf8'),
                              article.readCount,
                              article.likeCount,
                              time.strftime(ISOTIMEFORMAT, time.localtime(article.publishDateTime)),
                              '',
                              '',
                              '',
                              ''
                             )
                            )
            for comment in article.commentList:
                writer.writerow(
                                (
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    comment.commenterNickName.encode('utf8'),
                                    comment.content.encode('utf8'),
                                    comment.likeCount,
                                    time.strftime(ISOTIMEFORMAT, time.localtime(comment.createTime))
                                 )
                                )
        csvfile.close()
        
class Comment(object):
    def __init__(self):
        self.commenterNickName = ''
        self.likeCount = 0
        self.content = ''
        self.contentId = ''
        self.createTime = 0
        self.replyList = list()

class Reply(object):
    def __init__(self):
        self.replyId = 0
        self.content = ''
        self.createTime = 0
        self.uin = 0
        self.toUin = 0        
    
class Article(object):
    def __init__(self):
        self.userId = ''
        self.userName = ''
        self.wid = ''
        self.title = ''
        self.content =''
        self.contentUrl = ''        
        self.sourceUrl = ''
        self.digest = ''
        self.author = ''
        self.fileid = ''
        self.publishDateTime = 0
        self.commentList = list()
        self.readCount = -1
        self.likeCount = -1        

if __name__ == '__main__':
    import platform
    if 'window' in platform.system().lower():
        Logging.initLogger(os.path.join('conf','logging.win.cfg'))
    else:
        Logging.initLogger(os.path.join('conf','logging.cfg'))
    c = Configuration(os.path.join('conf',APP_NAME+'.cfg'))
    conf = c.readConfig()
    dbConf = conf[APP_NAME]['dbConf']

    logger = Logging.getLogger(APP_NAME)
    
    ownerList = conf[APP_NAME]['ownerList']
    for owner in ownerList:
        wc = WeiXinCralwer([2,5],logger)
        articleList = wc.crawl(owner)
        wc.writeDb(dbConf, owner, articleList)
    #wc.crawl('sysuyouth')
    #wc.crawl('sysudin')
    #wc.crawl('cuckoonews')
    #wc.crawl('shangxuele001')
    #wc.crawl('SYSU-KLY')
    
    #wc.crawl('gh_17311a0e8b0d')
    #wc.crawl('zdxyt666')
    #wc.crawl('Tan-talk')