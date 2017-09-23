import os
import sys
sys.path.append(sys.argv[0][:sys.argv[0].rfind(os.path.join('com','naswork'))])

import re
import base64
import json
import urllib
import binascii
import requests
import rsa
import time
from bs4 import BeautifulSoup
from com.naswork.sentiment.crawler.sessioncrawler import SessionCrawler
from com.naswork.sentiment.common.utils import MySqlProxy, Logging, Configuration
import datetime

add_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
APP_NAME = 'weibo'
AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
HEADER = {
    'User-Agent': AGENT,
    'Host': "login.sina.com.cn",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en,zh;q=0.8,zh-CN;q=0.6",
    "Connection": "keep-alive",
    "Cache-Control":"max-age=0",
    #"Content-Type":"application/x-www-form-urlencoded",
    #"Referer":"http://weibo.com/login.php",
    "Upgrade-Insecure-Requests":"1"
}
PRE_LOGIN_URL = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=%d'
LOGON_URL = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

def parseTopics(element):
    aTopicList = element.findAll('a',{'extra-data':'type=topic'})
    return map(lambda x: x.text.strip('#'), aTopicList)

class SinaWeiboLogon(object):
    def __init__(self, userName, password):
        self.logger = Logging.getLogger(APP_NAME)
        self.userName = userName
        self.password = password
        self.encryptedUserName = self.getEncryptedUserName()
        self.session = requests.session()
    
    def getEncryptedUserName(self):
        username_urllike   = urllib.quote(self.userName)
        #username_encrypted = base64.b64encode(bytes(username_urllike,encoding='utf-8'))
        username_encrypted = base64.b64encode(username_urllike.encode(encoding="utf-8")) 
        return username_encrypted.decode('utf-8')
    
    def fetchPreLogonContent(self):
        currentTime = time.time()*1000
        preLogonUrl = PRE_LOGIN_URL % (urllib.quote(self.encryptedUserName), currentTime)
        result = self.session.get(preLogonUrl)
        return result.text
    
    def parsePreLogonContent(self, content):
        json_pattern = re.compile('\((.*)\)')
        json_data_str = json_pattern.search(content).group(1)
        data = json.loads(json_data_str)
        return data
    
    def getEncryptedPassword(self, preLogonDataDict):
        rsa_e = 65537 #0x10001
        pw_string = str(preLogonDataDict['servertime']) + '\t' + str(preLogonDataDict['nonce']) + '\n' + str(self.password)
        key = rsa.PublicKey(int(preLogonDataDict['pubkey'],16),rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        passwd = binascii.b2a_hex(pw_encypted)
        return passwd
    
    def build_post_data(self, preLogonDataDict):
        post_data = {
            "entry":"weibo",
            "gateway":"1",
            "from":"",
            "savestate":"0",
            "useticket":"1",
            "pagerefer":"http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf":"1",
            "su":self.encryptedUserName,
            "service":"miniblog",
            "servertime":preLogonDataDict['servertime'],
            "nonce":preLogonDataDict['nonce'],
            "pwencode":"rsa2",
            "rsakv":preLogonDataDict['rsakv'],
            "sp":self.getEncryptedPassword(preLogonDataDict),
            "sr":"1366*768",
            "encoding":"UTF-8",
            "prelt":"24",
            "url":"http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype":"META"
        }
        return post_data
    
    def login(self):
        preLogonContent = self.fetchPreLogonContent()
        preLogonDataDict = self.parsePreLogonContent(preLogonContent)
        post_data = self.build_post_data(preLogonDataDict)
        result = self.session.post(LOGON_URL, post_data)
        print result.text
        p = re.compile('location\.replace\(\'(.*?)\'\)')
        login_url = p.search(result.text).group(1)
        # print login_url
        #redirect
        result = self.session.get(login_url)
        p2 = re.compile(r'"userdomain":"(.*?)"')
        home_url = 'http://weibo.com/' + p2.search(result.text).group(1)
        self.logger.info('Success to login')
        return self.session.get(home_url).text

def writeDb(dbConf, blogDict, logger):
    dbProxy = MySqlProxy(host=dbConf['dbHost'], 
                         port=3306, user=dbConf['dbUser'], 
                         passwd=dbConf['dbPasswd'], db=dbConf['dbName'])
    
    blogValueList = list()
    commentValueList = list()
    atValueList = list()
    topicValueList = list()
    
    blogSql = '''INSERT INTO T_SINABLOG (userid,userName,mid,content,add_datetime,
                    publish_datetime,publish_method,forward_mid,
                    forward_count,comment_count,like_count)
                values 
            '''
    # blogSql1 = "ON DUPLICATE KEY UPDATE forward_count=VALUES(forward_count),comment_count=VALUES(comment_count),like_count=VALUES(like_count)"

    commentSql = '''INSERT INTO T_SINABLOG_COMMENT (mid,cid,content,
            userid,userName, publish_datetime,like_count) values             
    '''
    atSql = 'INSERT INTO R_SINABLOG_ATNAME (mid,atname) values '
    topicSql = 'INSERT INTO R_SINABLOG_TOPIC (mid,topicname) values '
    
    blogMidSet = set(blogDict.keys())
    for blog in blogDict.values():
        if blog.forwardedBlog!=None:
            blogValueList.append(
                        '("%s","%s","%s","%s","%s","%s","%s","%s",%d,%d,%d)' %(
                            blog.userId, blog.nickName, blog.mid,
                            blog.content.strip().replace('"','\\"').replace("'", "''").replace("%", "\%").replace(":", "\:"),
                            add_datetime,
                            blog.publishDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                            blog.publishMethod, blog.forwardedBlog.mid,
                            blog.forwardCount, blog.commentCount, blog.likeCount 
                            )
                        )
            if blog.forwardedBlog.mid in blogDict or blog.forwardedBlog.mid in blogMidSet:
                logger.debug('Blog exists:%s', blog.forwardedBlog.mid)
            else:
                blogMidSet.add(blog.forwardedBlog.mid)
                blogValueList.append(
                        '("%s","%s","%s","%s","%s","%s","%s",null,%d,%d,%d)' %(
                            blog.forwardedBlog.userId, blog.forwardedBlog.nickName.replace('"','\\"'), blog.forwardedBlog.mid,
                            blog.forwardedBlog.content.strip().replace('"','\\"').replace("'", "''").replace("%", "\%").replace(":", "\:"),
                            add_datetime,
                            blog.forwardedBlog.publishDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                            blog.forwardedBlog.publishMethod.replace('"','\\"'), 
                            blog.forwardedBlog.forwardCount, blog.forwardedBlog.commentCount, blog.forwardedBlog.likeCount 
                            )
                        )
            for topic in blog.forwardedBlog.topicList:
                topicValueList.append('("%s","%s")'%(blog.forwardedBlog.mid, topic))
            for atName in blog.forwardedBlog.atNameList:
                atValueList.append('("%s","%s")'%(blog.forwardedBlog.mid, atName))
        else:
            blogValueList.append(
                        '("%s","%s","%s","%s","%s","%s","%s",null,%d,%d,%d)' %(
                            blog.userId, blog.nickName.replace('"','\\"'), blog.mid,
                            blog.content.strip().replace('"','\\"').replace("'", "''").replace("%", "\%").replace(":", "\:"),
                            add_datetime,
                            blog.publishDateTime.strftime('%Y-%m-%d %H:%M:%S'),
                            blog.publishMethod.replace('"','\\"'), 
                            blog.forwardCount, blog.commentCount, blog.likeCount 
                            )
                        )

        for comment in blog.commentList:
            commentValueList.append('("%s","%s","%s","%s","%s","%s",%d)' %(
                                        blog.mid, comment.cid, 
                                        comment.content.replace('"','\\"'), 
                                        comment.userId, comment.userName.replace('"','\\"'), 
                                        comment.publishDateTime.strftime('%Y-%m-%d %H:%M:%S'), comment.likeCount))
        for topic in blog.topicList:
            topicValueList.append('("%s","%s")'%(blog.mid, topic.replace('"','\\"')))
        for atName in blog.atNameList:
            atValueList.append('("%s","%s")'%(blog.mid, atName.replace('"','\\"')))
    
    #clear the db firstly
    sql = 'delete from T_SINABLOG_COMMENT where mid in (%s)' % (','.join(map(lambda x: '"'+x+'"', blogMidSet)))
    dbProxy.execute(sql)
    sql = 'delete from R_SINABLOG_TOPIC where mid in (%s)' % (','.join(map(lambda x: '"'+x+'"', blogMidSet)))
    dbProxy.execute(sql)
    sql = 'delete from R_SINABLOG_ATNAME where mid in (%s)' % (','.join(map(lambda x: '"'+x+'"', blogMidSet)))
    dbProxy.execute(sql)
    sql = 'delete from T_SINABLOG where mid in (%s)' % (','.join(map(lambda x: '"'+x+'"', blogMidSet)))
    dbProxy.execute(sql)
    
    #insert to db
    BATCH_SIZE = 500
    if len(blogValueList)>0:
        logger.info('Insert %d records to blog', len(blogValueList))
        index = 0
        while index<len(blogValueList):
            dbProxy.execute(blogSql +','.join(blogValueList[index:min(index+BATCH_SIZE,len(blogValueList))-1]))
            index+=BATCH_SIZE
            dbProxy.commit()
        
    if len(commentValueList)>0:
        logger.info('Insert %d records to comment', len(commentValueList))
        index = 0
        while index<len(commentValueList):
            dbProxy.execute(commentSql +','.join(commentValueList[index:min(index+BATCH_SIZE,len(commentValueList))-1]))
            index+=BATCH_SIZE
            dbProxy.commit()

    if len(atValueList)>0:
        logger.info('Insert %d records to atName', len(atValueList))
        index = 0
        while index<len(atValueList):
            dbProxy.execute(atSql +','.join(atValueList[index:min(index+BATCH_SIZE,len(atValueList))-1]))
            index+=BATCH_SIZE
            dbProxy.commit()
    if len(topicValueList)>0:
        logger.info('Insert %d records to topic', len(topicValueList))
        index = 0
        while index<len(topicValueList):
            dbProxy.execute(topicSql +','.join(topicValueList[index:min(index+BATCH_SIZE,len(topicValueList))-1]))
            index+=BATCH_SIZE
            dbProxy.commit()
    # dbProxy.commit()

MORE_CONTENT_URL = 'http://s.weibo.com/ajax/direct/morethan140?%s'

def getMoreContentData(session, action_data):
    url = MORE_CONTENT_URL % action_data    
    session.randomSleep()
    content = session.get(url)
    jo = json.loads(content)
    data = jo['data']['html']
    return data
    
BLOG_SEARCH_PAGE = 'http://s.weibo.com/weibo/%s&page=%d'
BLOG_SEARCH_ALL_PAGE = 'http://s.weibo.com/weibo/%s&scope=ori&suball=1&page=%d&timescope=custom:2017-01-01:'
class SinaWeiboSearchCrawler(object):
    def __init__(self, session):
        self.logger = Logging.getLogger(APP_NAME)
        self.session = session
        self.done = False
    
    def searchMainPage(self, keyword, pageNum):
        '''
        @param keyword: keyword must be in utf8 encoding 
        '''
        url = BLOG_SEARCH_ALL_PAGE % (urllib.quote(urllib.quote(keyword)), pageNum)
        print url
        content = self.session.get(url)
        lindex = content.find('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct"')
        rindex = content[lindex:].find('</script>')
        rindex = lindex + rindex - 1
        lindex = lindex + len('<script>STK && STK.pageletM && STK.pageletM.view(')
        jo = json.loads(content[lindex:rindex])
        data = jo['html']
        return data
    
    def parseData(self, data):
        blogDict = dict()
        soup = BeautifulSoup(data)
        divFeedListItemList = soup.findAll('div',{'action-type':'feed_list_item'})
        for divFeedListItem in divFeedListItemList:
            b = Blog()
            b.mid = divFeedListItem['mid']
            divFeedDetail = divFeedListItem.findAll('div',{'class':'WB_feed_detail clearfix'})[0]
            #face to find userId & nickname
            divFace = divFeedDetail.findAll('div',{'class':'face'})[0]
            img = divFace.findAll('img')[0]
            b.nickName = img['alt']
            userCard = img['usercard']
            p = re.compile('id=\d+')
            b.userId = p.search(userCard).group(0)[3:]
            
            #content
            pContent = divFeedDetail.findAll('p',{'node-type':'feed_list_content'})[0]
            aMoreList = pContent.findAll('a',{'action-type':"fl_unfold"}) 
            if len(aMoreList)>0:
                url = MORE_CONTENT_URL % aMoreList[0]['action-data']
                b.content = self.getMoreContent(url)
            else:
                b.content = pContent.text

            #feed from
            divFeedFrom = divFeedDetail.findAll('div',{'class':'feed_from W_textb'})[0]
            aDateTime = divFeedFrom.findAll('a',{'node-type':'feed_list_item_date'})[0]
            b.publishDateTime = datetime.datetime.fromtimestamp(
                                                int(aDateTime['date'])/1000)
            if divFeedFrom.text.find(u'\u6765\u81ea')>0:
                b.publishMethod = aDateTime.findNext('a').text

            #forward count
            aForward = divFeedListItem.findAll('a',{'action-type':'feed_list_forward'})[0]
            try:
                b.forwardCount = int(aForward.text.replace(u'\u8f6c\u53d1',''))
            except:
                b.forwardCount = 0

            #comment count
            aComment = divFeedListItem.findAll('a',{'action-type':'feed_list_comment'})[0]
            try:
                b.commentCount = int(aComment.text.replace(u'\u8bc4\u8bba',''))
            except:
                b.commentCount = 0
            #like count
            aLike = divFeedListItem.findAll('a',{'action-type':'feed_list_like'})[0]
            try:
                b.likeCount = int(aLike.text)
            except:
                b.likeCount = 0
            blogDict[b.mid] = b
        return blogDict
    
    def getMoreContent(self, url):
        self.session.randomSleep()
        content = self.session.get(url)
        jo = json.loads(content)
        data = jo['data']['html']
        soup = BeautifulSoup(data, 'html.parser')
        return soup.text
    
    def search(self, keyword, startPage, endPage):
        '''
        @param keyword: keyword must be in utf8 encoding 
        '''
        pageNum = startPage
        blogDict = dict()
        while pageNum <= endPage:
            data = self.searchMainPage(keyword, pageNum)
            pageNum += 1
            blogDict.update(self.parseData(data))
        
        return blogDict

BLOG_MAIN_PAGE_URL_DIGITAL_OWNER = 'http://weibo.com/u/%s?pids=Pl_Official_MyProfileFeed__%d&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%d&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=%%2Fu%%2F%s%%3Fis_all%%3D1&_t=FM_%d'
BLOG_MAIN_PAGE_URL_NON_DIGITAL_OWNER = 'http://weibo.com/%s?pids=Pl_Official_MyProfileFeed__%d&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%d&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=%%2F%s%%3Fis_all%%3D1&_t=FM_%d'
BLOG_SUB_PAGE_URL = 'http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&profile_ftype=1&is_all=1&pagebar=%d&pl_name=Pl_Official_MyProfileFeed__%d&id=%s&script_uri=/u/%s&feed_type=0&page=%d&pre_page=%d&domain_op=%s&__rnd=%d'
class SinaWeiboListCrawler(object):
    def __init__(self, session, startDate, endDate):
        '''
        @param startDate: yyyy-mm-dd, crawl all blogs no earlier than the specified startDate 
        '''
        self.logger = Logging.getLogger(APP_NAME)
        self.startDate = datetime.datetime.strptime(startDate,"%Y-%m-%d")
        self.endDate = datetime.datetime.strptime(endDate+' 23:59:59',"%Y-%m-%d %H:%M:%S")
        self.session = session
        self.done = False

    def queryBlog(self, ownerId, ownerIdNonDigit, ownerIdType, pid, domain):
        pageNum = 1
        blogDict = dict()
        while self.done is False:
            self.logger.debug('Query main page %d for %s', pageNum, ownerId)
            data = self.queryMainPage(ownerId, ownerIdNonDigit, ownerIdType, pid, pageNum)
            if pageNum==1:
                blogDict.update(self.parseBlogList(ownerId, data, ignoreFirst=True))
            else:
                blogDict.update(self.parseBlogList(ownerId, data))
            if self.done:
                break
            for subPage in (0,1):
                self.logger.debug('Query subpage %d of %d for %s', subPage, pageNum, ownerId)
                data = self.querySubPage(ownerId, pid, domain, pageNum, subPage)
                blogDict.update(self.parseBlogList(ownerId, data))
                if self.done:
                    break            
            if self.done:
                break
            pageNum+=1
        return blogDict

    def queryMainPage(self, ownerId, ownerIdNonDigit, ownerIdType, pid, pageNum):
        self.session.randomSleep()
        if ownerIdType == 0:
            url = BLOG_MAIN_PAGE_URL_DIGITAL_OWNER % (ownerId, pid, pageNum, ownerId, int(time.time()*1000))
        else:
            url = BLOG_MAIN_PAGE_URL_NON_DIGITAL_OWNER % (ownerIdNonDigit, pid, pageNum, ownerIdNonDigit, int(time.time()*1000))
        content = self.session.get(url)
        lindex = content.find('<script>parent.FM.view({"ns":"pl.content.homeFeed.index","domid":"Pl_Official_MyProfileFeed__%d"'%pid)
        rindex = content[lindex:].find('</script>')
        rindex = lindex + rindex - 1
        lindex = lindex + len('<script>parent.FM.view(')
        jo = json.loads(content[lindex:rindex])
        data = jo['html']
        return data
    
    def querySubPage(self, ownerId, pid, domain, mainPageNum, subPageNum):
        id = domain+ownerId
        blogListUrl = BLOG_SUB_PAGE_URL % (domain, subPageNum, pid, id, ownerId, mainPageNum, mainPageNum, domain, int(time.time()*1000))
        
        #oriBlogListUrl = BLOG_LIST_ORIG_URL % (domain, pageNum, id, ownerId, domain, int(time.time()*1000))
        self.session.randomSleep()
        content = self.session.get(blogListUrl)
        #content = self.session.get(oriBlogListUrl).text
        jo = json.loads(content)
        data = jo['data']
        return data
         
    def parseAtNames(self, element):    
        aAtNameList = element.findAll('a',{'extra-data':'type=atname'})
        return map(lambda x: x.text.strip('@'), aAtNameList)
    
    def parsePublishInfo(self, element):
        divFrom = element.findAll('div',{'class':'WB_from S_txt2'})[0]
        aDateTime = element.findAll('a',{'node-type':'feed_list_item_date'})[0]
        if divFrom.text.find(u'\u6765\u81ea')>0:
            publishMethod = aDateTime.findNext('a').text
        else:
            publishMethod = ''
        #print aDateTime['date']
        #return (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(aDateTime['date'])/1000)), aPublishMethod.text)
        return (datetime.datetime.fromtimestamp(
                                                int(aDateTime['date'])/1000), publishMethod)
    
    def parseBlogList(self, ownerId, data, ignoreFirst=False):

        blockDict = dict()
        soup = BeautifulSoup(data)
        divFeedListItemList = soup.findAll('div',{'action-type':'feed_list_item'})
        isFirst = True
        for divFeedListItem in divFeedListItemList:
            b = Blog()
            b.mid = divFeedListItem['mid'] #message id
            b.userId = ownerId
            #1. content
            divFeedContent = divFeedListItem.findAll('div',{'node-type':'feed_list_content'})[0]
            try:
                #TODO nickname may not exists if from others
                b.nickName = divFeedContent['nick-name']
            except:                
                #in current implementation, ignore the blog that is not generated by the user
                #print 'Skip:nick-name not found for '+b.mid 
                pass
            
            #check if its own or liked one
            iList = divFeedListItem.findAll('i',{'class':'W_ficon ficon_praised S_ficon'})
            if len(iList)>0:
                #this is the one that the author praised on instead of his own so the datetime may be different
                #currently just skip this one but not stop
                self.logger.debug('Skip: for praised one %s', b.mid)
                continue
            #2. publish date time & method
            (b.publishDateTime, b.publishMethod) = self.parsePublishInfo(divFeedListItem)
            if b.publishDateTime<self.startDate:
                
                if isFirst and not ignoreFirst:
                    self.logger.debug('publishDateTime %s is less than startDate for %s', str(b.publishDateTime),b.mid)
                    self.done = True
                    break
                elif not isFirst:
                    self.logger.debug('publishDateTime %s is less than startDate for %s', str(b.publishDateTime),b.mid)
                    self.done = True
                    break
            if b.publishDateTime > self.endDate:
                #just skip if it is not in range
                continue
            if isFirst:
                isFirst = False
            #print 'PublishDateTime:'+str(b.publishDateTime)
            #1) find topics under the content
            b.topicList = parseTopics(divFeedContent)
            #2) find at names
            b.atNameList = self.parseAtNames(divFeedContent)
            #3) content
            b.content = divFeedContent.text.replace(u'\u200b','').replace(u'\xa0','').strip('\n').strip()

            #4. check if it is forwarded
            dForwardList = divFeedListItem.findAll('div',{'node-type':'feed_list_forwardContent'})
            isForwarded = False
            if len(dForwardList)>0:
                dForward = dForwardList[0]

                aOriginList = dForward.findAll('a',{'node-type':'feed_list_originNick'})
                if len(aOriginList) == 0:
                    #the forwarded blog might be deleted
                    self.logger.debug('The forwarded content by Blog %s might have been deleted', b.mid)
                else:
                    b.forwardedBlog = Blog()
                    isForwarded = True
                    aOrigin = aOriginList[0]
                    b.forwardedBlog.nickName = aOrigin['nick-name']
                    hrefStr = aOrigin['href']
                    if hrefStr.startswith('/u/'):
                        b.forwardedBlog.userId= hrefStr[3:hrefStr.find('?')]
                    else:
                        b.forwardedBlog.userId = hrefStr[1:hrefStr.find('?')]
                    divFeedListReason = dForward.findAll('div',{'node-type':'feed_list_reason'})[0]
                    b.forwardedBlog.content = divFeedListReason.text.replace(u'\u200b','').replace(u'\xa0','').strip('\n').strip()
                    b.forwardedBlog.atNameList = self.parseAtNames(dForward)
                    b.forwardedBlog.topicList = parseTopics(dForward)
                    
                    #forward
                    preForwardEm = dForward.findAll('em',{'class':'W_ficon ficon_forward S_ficon'})[0]
                    forwardEm = preForwardEm.findNext('em')
                    try:
                        b.forwardedBlog.forwardCount=int(forwardEm.text)
                    except:
                        b.forwardedBlog.forwardCount=0
                    #comment
                    preCommentEm = dForward.findAll('em',{'class':'W_ficon ficon_repeat S_ficon'})[0]
                    commenEm = preCommentEm.findNext('em')
                    try:
                        b.forwardedBlog.commentCount = int(commenEm.text)
                    except:
                        b.forwardedBlog.commentCount = 0
                    
                    #like
                    preALikeEm = dForward.findAll('em',{'class':'W_ficon ficon_praised S_txt2'})[0]
                    aLikeEm = preALikeEm.findNext('em')
                    try:
                        b.forwardedBlog.likeCount = int(aLikeEm.text)
                    except:
                        b.forwardedBlog.likeCount = 0
                    
                    #mid
                    aLike = dForward.findAll('a',{'action-type':'fl_like'})[0]
                    action_data = aLike['action-data']
                    midIndex= action_data.find('mid=')
                    b.forwardedBlog.mid = action_data[midIndex+4:]
                    
                    #datetime & method
                    (b.forwardedBlog.publishDateTime, b.forwardedBlog.publishMethod) = self.parsePublishInfo(dForward) 
                
            #forward
            aForward = divFeedListItem.findAll('a',{'action-type':'fl_forward'})[0]
            try:
                b.forwardCount = int(aForward.text.replace(u'\ue607',''))
            except:
                b.forwardCount = 0

            #comment
            aComment = divFeedListItem.findAll('a',{'action-type':'fl_comment'})[0]
            try:
                b.commentCount = int(aComment.text.replace(u'\ue608',''))
            except:
                b.commentCount = 0
            #like
            if isForwarded:
                aLike = divFeedListItem.findAll('a',{'action-type':'fl_like'})[1]
            else:
                aLike = divFeedListItem.findAll('a',{'action-type':'fl_like'})[0]
            try:
                b.likeCount = int(aLike.findAll('em')[1].text)
            except:
                b.likeCount = 0
            blockDict[b.mid] = b
            
        return blockDict

#COMMENT_URL = 'http://weibo.com/aj/v6/comment/small?ajwvr=6&act=list&mid=%s&uid=%s&isMain=true&dissDataFromFeed=%%5Bobject%%20Object%%5D&ouid=%s&location=page_%s_home&comment_type=0&_t=0&__rnd=%d'
#COMMENT_URL = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&from=singleWeiBo&__rnd=%d'
#COMMENT_BY_TIME_URL = 'http://weibo.com/aj/v6/comment/small?ajwvr=6&mid=%s&filter=all&__rnd=%d'
LIKE_URL = 'http://weibo.com/aj/like/object/big?ajwvr=6&object_id=%s&object_type=comment&_t=0&__rnd=%d'
COMMENT_BY_TIME_URL = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&filter=all&from=singleWeiBo&__rnd=%d'
class SinaWeiboCommentCrawler(object):
    def __init__(self, session):
        self.logger = Logging.getLogger(APP_NAME)
        self.session = session
    
    def queryComment(self, mid):    
        commentList = list()
        url = COMMENT_BY_TIME_URL % (mid, int(time.time()*1000))
        while url:
            self.session.randomSleep()
            content = self.session.get(url)
            url = self.parseComment(content, commentList)

        return commentList
    def parseComment(self, content, commentList):
        jo = json.loads(content)
        html = jo['data']['html']
        soup = BeautifulSoup(html)
        divCommentList = soup.findAll('div',{'node-type':'root_comment'})
        for divComment in divCommentList:
            comment = Comment()
            #cid
            comment.cid = divComment['comment_id']
            #find commenter id
            divFace = divComment.findAll('div',{'class':'WB_face W_fl'})[0]
            img = divFace.findAll('img')[0]
            comment.userId = img['usercard'][3:]
            #find commenter name
            dtext = divComment.findAll('div',{'class':'WB_text'})[0]
            ahref = dtext.findAll('a')[0]
            comment.userName = ahref.text
            comment.content = dtext.text.replace(ahref.text+u'\uff1a','').strip('\n').strip()
            
            #likeCount
            emLike = divComment.findAll('em',{'class':'W_ficon ficon_praised S_txt2'})[0]
            try:
                comment.likeCount = int(emLike.findNext('em').text)
            except:
                comment.likeCount = 0
            #publishDate (in chinese format)
            comment.publishDateTime = self.parseDateTime(divComment.findAll('div',{'class':'WB_from S_txt2'})[0].text)
            #by default, no need to fetch like list
            #comment.likeUserList = self.fetchLikeList(comment.cid)
            commentList.append(comment)
        
        divCommentLoadingList = soup.findAll('div',{'node-type':'comment_loading'})
        if len(divCommentLoadingList)==0:
            return None
        else:
            return 'http://weibo.com/aj/v6/comment/big?ajwvr=6&' + divCommentLoadingList[0]['action-data'] +'&from=singleWeiBo&__rnd=%d'%(time.time()*1000)
    
    def parseDateTime(self, datetimeStr):
        if datetimeStr.find(u'\u79d2\u524d')>0:
            secondsDelta = float(datetimeStr.replace(u'\u79d2\u524d',''))
            return datetime.datetime.now()-datetime.timedelta(seconds=secondsDelta)
        if datetimeStr.find(u'\u5206\u949f\u524d')>0:            
            secondsDelta = float(datetimeStr.replace(u'\u5206\u949f\u524d',''))*60
            return datetime.datetime.now()-datetime.timedelta(seconds=secondsDelta)
        if datetimeStr.find(u'\u4eca\u5929')>=0:
            datetimeStr=datetime.datetime.today().strftime('%Y-%m-%d')+datetimeStr.replace(u'\u4eca\u5929','')
            return datetime.datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M')
        if datetimeStr.find(u'\u6708')>=0:
            datetimeStr=str(datetime.datetime.today().year)+'-'+datetimeStr.replace(u'\u6708','-').replace(u'\u65e5','')
            return datetime.datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M')
        return datetime.datetime.strptime(datetimeStr, '%Y-%m-%d %H:%M')
    def fetchLikeList(self, commentId):
        url = LIKE_URL % (commentId, int(time.time()*1000))
        self.session.randomSleep()
        content = self.session.get(url)
        jo = json.loads(content)
        html = jo['data']['html']
        soup = BeautifulSoup(html)
        liList = soup.findAll('li')
        likeList = list()
        for li in liList:
            nickName = li.findAll('img')[0]['alt']
            likeList.append({'uid':li['uid'],'nick-name':nickName})
        return likeList
    
class Comment(object):
    def __init__(self):
        self.cid = ''
        self.userId = ''
        self.userName=''        
        self.content = ''
        self.publishDateTime = ''
        self.likeCount = -1
        self.replyList = list()
        self.likeUserList = list()

class Reply(object):
    def __init__(self):
        pass        
class Blog(object):
    def __init__(self):
        self.content = ''
        self.publishDateTime = ''
        self.publishMethod = ''
        self.userIdNoDigit = ''
        self.userId = ''
        self.nickName = '' # may not necessarily by the blogger
        self.mid = ''#msg id            
        self.forwardCount = -1
        self.commentCount = -1
        self.likeCount = -1
        self.topicList = list()
        self.atNameList = list()
        self.forwardedBlog = None
        self.commentList = list()

#query by topic
if __name__ == '__main__':
    import platform
    if 'window' in platform.system().lower():
        Logging.initLogger(os.path.join('conf','logging.win.cfg'))
    else:
        Logging.initLogger(os.path.join('conf','logging.cfg'))
    c = Configuration(os.path.join('conf',APP_NAME+'.cfg'))
    conf = c.readConfig()
    dbConf = conf[APP_NAME]['dbConf']
    search = conf[APP_NAME]['search']
    #keyword = search['keyword']
    keyword = u"\u4e2d\u5c71\u5927\u5b66".encode('utf-8')
    startPage = int(search['startPage'])
    endPage = int(search['endPage'])
    logger = Logging.getLogger(APP_NAME)
    sinaUser = conf[APP_NAME]['sinaUser']
    sinaPassword = conf[APP_NAME]['sinaPassword']
    l = SinaWeiboLogon(sinaUser,sinaPassword)
    logincontent=l.login()
    s = SessionCrawler(l.session,conf[APP_NAME]['sleepTime'], logger)
    ss = SinaWeiboSearchCrawler(s)
    sc = SinaWeiboCommentCrawler(s)
    startTime = time.time()
    blogDict = ss.search(keyword, startPage, endPage)
    logger.info('Begin to crawl comment. Totally %d to crawl', len(blogDict))
    count = 0
    for mid in blogDict:
        #logger.debug('Begin to crawl comment %s for %s', mid, owner['ownerIdDigit'])
        count+=1
        if count % 20 == 0:
            logger.debug('Finish crawl %d comment', count)
        blogDict[mid].commentList = sc.queryComment(mid)
    writeDb(dbConf, blogDict, logger)
    endTime = time.time()
    logger.info('Finish crawling %s within %s minute for page %d to %d', 
                keyword.decode('utf-8'),
                round((endTime-startTime)/60,2),
                startPage,
                endPage)
#query by accounts
'''
if __name__ == '__main__':
    import platform
    if 'window' in platform.system().lower():
        Logging.initLogger(os.path.join('conf','logging.win.cfg'))
    else:
        Logging.initLogger(os.path.join('conf','logging.cfg'))

    c = Configuration(os.path.join('conf',APP_NAME+'.cfg'))
    conf = c.readConfig()
    dbConf = conf[APP_NAME]['dbConf']
    startDate = conf[APP_NAME]['startDate']
    endDate = conf[APP_NAME]['endDate']
    logger = Logging.getLogger(APP_NAME)
    sinaUser = conf[APP_NAME]['sinaUser']
    sinaPassword = conf[APP_NAME]['sinaPassword']
    l = SinaWeiboLogon(sinaUser,sinaPassword)
    logincontent=l.login()
    s = SessionCrawler(l.session,conf[APP_NAME]['sleepTime'], logger)
    ownerList = conf[APP_NAME]['ownerList']
    sc=SinaWeiboCommentCrawler(s)
    for owner in ownerList:
        startTime = time.time()
        blogListCrawler = SinaWeiboListCrawler(s, startDate, endDate)
        blogDict = blogListCrawler.queryBlog(owner['ownerIdDigit'], owner['ownerIdNonDigit'],owner['ownerIdType'], owner['pid'], owner['domain'])

        logger.info('Begin to crawl comment for %s. Totally %d to crawl', owner['ownerIdDigit'], len(blogDict))
        count = 0
        for mid in blogDict:
            #logger.debug('Begin to crawl comment %s for %s', mid, owner['ownerIdDigit'])
            count+=1
            if count % 20 == 0:
                logger.debug('Finish crawl %d comment for %s', count, owner['ownerIdDigit'])
            blogDict[mid].commentList = sc.queryComment(mid)

        writeDb(dbConf, owner['ownerIdDigit'],blogDict,logger)
        logger.info('Finish writing db for %s', owner['ownerIdDigit'])
        endTime = time.time()
        logger.info('Finish crawling %s within %s minute for time range:%s to %s',
                    owner['ownerIdDigit'],
                    round((endTime-startTime)/60,2),
                    startDate,
                    endDate)
'''