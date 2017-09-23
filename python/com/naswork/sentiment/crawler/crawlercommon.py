'''
Created on Jan 9, 2015

@author: eyaomai
'''
import urllib2
import re
import datetime
import time
import random
import traceback
from com.naswork.sentiment.common.utils import RequestHandler, Logging, Audit, OneTimeThread,MySqlProxy,StoppableThread,\
    CTPUtils

class CrawlerCommon(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        pass
    @staticmethod
    def toDate(datestr, default='1981-01-01'):
        if datestr is None:
            datetime_instance = datetime.datetime.strptime(default, '%Y-%m-%d')
        else:
            datetime_instance = datetime.datetime.strptime(datestr, '%Y-%m-%d')
        return datetime.date(datetime_instance.year,datetime_instance.month, datetime_instance.day)
     
    @staticmethod
    def readContent(url, withHeaders=False, data=None):
        conn = CrawlerCommon.getConnWithHeaders(url, withHeaders, data)
        if conn is None:
            return '','Fail to establish url conn'
        html = conn.read()
        pattern="charset=.*?\""
        charset_groups = re.search(pattern, html)
        charset = 'utf-8'
        warning_str = None
        if charset_groups is not None:
            charset_str = charset_groups.group(0)
            charset = charset_str[charset_str.index('=')+1:len(charset_str)-1]
        else:
            warning_str = 'charset not found'
        
        ss = set(['gb2312','gbk','utf-8'])
        if warning_str is not None:
            ss.remove(charset)
        charset_list = list(ss)
        if warning_str is not None:
            charset_list.insert(0,charset)
        failure = False
        successCharset = ''
        content = html
        for charset_i in charset_list:
            try:
                content = unicode(html,charset_i)
                if failure:
                    successCharset = charset_i
                break
            except UnicodeDecodeError:
                if failure is False:
                    failure = True                
                continue    
        if failure:            
            if successCharset == '':
                content = unicode(html, charset, 'ignore')
                if warning_str:
                    warning_str +=' Can not decode'
                else:
                    warning_str = 'Charset was declared as %s with some character decode error ignored' % charset
            else:
                warning_str ='Charset was declared as %s but is actually %s' % (charset, successCharset)
        return content.encode('utf-8'), warning_str                

    @staticmethod
    def initUrlLib():
        import cookielib, urllib2
        cj = cookielib.CookieJar()
        proxy_handler = urllib2.ProxyHandler({'http': 'www-proxy.ao.ericsson.se:8080'})
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),proxy_handler)
        urllib2.install_opener(opener)
        return cj
    @staticmethod
    def getConnWithHeaders(url, withHeaders=True, data=None):
        try:
            if withHeaders is False:
                conn = urllib2.urlopen(url,data)
            else:
                req = urllib2.Request(url,data)
                req.add_header("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
                req.add_header("Accept-Encoding","utf-8")
                req.add_header("Accept-Language","en-US,en;q=0.8,zh-CN;q=0.6")
                req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36")
                conn = urllib2.urlopen(req)
            return conn
        except Exception:
            traceInfo = traceback.format_exc()
            Logging.LOGGER.error('Fail to handle url (%s) with exception: %s',url, traceInfo)
            return None
class CrawlerConstants(object):
    PARA_CRAWLER_ID = 'identifier'
    
    PARA_STATUS = 'status'
    VAL_STATUS_FINISH = 'finish'
    VAL_STATUS_FAILURE = 'failure'
    VAL_STATUS_NOMORE = 'nomore'
    VAL_STATUS_STOP = 'stop'

    PARA_ACTION = 'action'    
    VAL_ACTION_NOTIFYDONE = 'notifyDone'
    VAL_ACTION_NOTIFYPARTIAL = 'notifyPartial'
    VAL_ACTION_AUDIT = 'audit'
    VAL_ACTION_CRAWL = 'crawl'

    PARA_AUDIT_PARAMETER = 'parameter'
    VAL_AUDIT_PARAMETER_CONFIG = 'config'
    VAL_AUDIT_PARAMETER_RECURRENCE = 'recurrence'
    
    PARA_TOTAL_TIME = 'totaltime'
    PARA_RESULT = 'result'
    PARA_TOTAL_NUM = 'totalNum'
    PARA_CLASS = 'class'
    CLASS_NAME_PATTERN = 'Crawler'
    
    CONFIG_FILE_SLEEP_RANGE = 'sleepRange'
    CONFIG_FILE_NUM_THREAD = 'numThread'
    CONFIG_FILE_NO_DB = 'noDB'
    CONFIG_FILE_DBHOST = 'dbHost'
    CONFIG_FILE_DBPORT = 'dbPort'
    CONFIG_FILE_DBUSER = 'dbUser'
    CONFIG_FILE_DBPASS = 'dbPasswd'
    CONFIG_FILE_DBNAME = 'dbName'
    CONFIG_FILE_FAILURE_TABLENAME = 'failureTableName'
    CONFIG_FILE_FAILURE_HANDLING = 'failureHandling'
    
    CONFIG_FILE_RECURRENCE='recurrence'
    CONFIG_FILE_ENABLE='enable'
    CONFIG_FILE_STARTTIME='startTime'
    CONFIG_FILE_DAILY='daily'
    CONFIG_FILE_WEEKLY='weekly'
    CONFIG_FILE_DAYOFWEEK='dayOfWeek'
    CONFIG_FILE_TRADE_DAY_ONLY = 'tradeDayOnly'
    
    CONFIG_FILE_DEBUG = 'DEBUG'

class CrawlerManager(RequestHandler):
    DAYOFWEEK = {"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5, "SUN":6}
    def __init__(self, json_config_file,sleep_time, failureUrlPattern, minimalThread=-1):
        '''
        Constructor
        '''
        super(CrawlerManager, self).__init__(sleep_time=sleep_time)
        self.logger = Logging.LOGGER
        self.__minimalThread = minimalThread
        self.__json_config_file = json_config_file
        self.__config = None
        self.__isValid = False
        self.__readConfig()
        self.__getCommonConfig()
        self._getNonCommonConfig(self.__config)
        self._validate()
        self.dbProxy = None
        if self._noDb is False:
            self.dbProxy = MySqlProxy(self._dbHost, self._dbPort, self._dbUser, self._dbPasswd, self._dbName, logger=self.logger)
        self.__configAudit = Audit(self, 60, CrawlerConstants.VAL_AUDIT_PARAMETER_CONFIG)
        self.__recurrenceAudit = None
        
        self.__totalTasks = 0
        self.__startTime = 0
        self.__workers = dict()
        self._taskList = list()
        
        self.__failureUrlPattern = failureUrlPattern
        self.__failureHandlingFlag = False
        self.__round = 0
        self.__maxTime = 0
    
    def __readConfig(self):
        className = self.__class__.__name__
        rindex = className.rfind('.')
        if rindex>=0:
            className = className[rindex+1:]
        self.__config = self.readConfig(self.__json_config_file)[className]
    
    def __getCommonConfig(self):
        self._numThread = self.__config[CrawlerConstants.CONFIG_FILE_NUM_THREAD]
        if self.__minimalThread>0 and self._numThread<self.__minimalThread:
            self._numThread = self.__minimalThread
        self.__sleepRange = self.__config[CrawlerConstants.CONFIG_FILE_SLEEP_RANGE]
        self._noDb = False
        if CrawlerConstants.CONFIG_FILE_NO_DB in self.__config:
            noDb = self.__config[CrawlerConstants.CONFIG_FILE_NO_DB]
            if noDb.lower().strip()=='true':
                self._noDb = True
        self.debug = False
        if CrawlerConstants.CONFIG_FILE_DEBUG in self.__config:
            if self.__config[CrawlerConstants.CONFIG_FILE_DEBUG].lower().strip()=='true':
                self.debug = True
        self._dbHost = self.__config[CrawlerConstants.CONFIG_FILE_DBHOST]
        self._dbPort = self.__config[CrawlerConstants.CONFIG_FILE_DBPORT]
        self._dbUser = self.__config[CrawlerConstants.CONFIG_FILE_DBUSER]
        self._dbPasswd = self.__config[CrawlerConstants.CONFIG_FILE_DBPASS]
        self._dbName = self.__config[CrawlerConstants.CONFIG_FILE_DBNAME]
        self.__failureTableName = self.__config[CrawlerConstants.CONFIG_FILE_FAILURE_TABLENAME]
        failureHandling = self.__config[CrawlerConstants.CONFIG_FILE_FAILURE_HANDLING]
        if failureHandling.strip().lower()=='true':
            self.__failureHandling = True
        else:
            self.__failureHandling = False
        
        self.__getAndCalculateRecurrence()
    
    def __getAndCalculateRecurrence(self):
        recurrenceEnable = self.__config[CrawlerConstants.CONFIG_FILE_RECURRENCE][CrawlerConstants.CONFIG_FILE_ENABLE]
        if recurrenceEnable.strip().lower()=='true':
            self.__recurrence = self.__config[CrawlerConstants.CONFIG_FILE_RECURRENCE]
        else:
            self.__recurrence = None

    def __getDeltaBeforeNextRun(self):
        now = datetime.datetime.now()
        if self.__recurrence is None:
            return (-1,now) 
        startTime = self.__config[CrawlerConstants.CONFIG_FILE_RECURRENCE][CrawlerConstants.CONFIG_FILE_STARTTIME]
        if startTime<=now.strftime('%H:%M:%S'):
            now = now+datetime.timedelta(days=1)
        nextPossible = datetime.datetime(now.year, now.month, now.day, int(startTime[:2]),int(startTime[3:5]), int(startTime[6:]))

        dailyConf = self.__config[CrawlerConstants.CONFIG_FILE_RECURRENCE][CrawlerConstants.CONFIG_FILE_DAILY]
        dailyEnable = dailyConf[CrawlerConstants.CONFIG_FILE_ENABLE]
        if dailyEnable.strip().lower()=='true':
            tradeDayOnly = dailyConf[CrawlerConstants.CONFIG_FILE_TRADE_DAY_ONLY]
            if tradeDayOnly.strip().lower()=='true':
                while(CTPUtils.Singleton.isHoliday(nextPossible)):
                    nextPossible = nextPossible + datetime.timedelta(1)
        else:
            weeklyConf = self.__config[CrawlerConstants.CONFIG_FILE_RECURRENCE][CrawlerConstants.CONFIG_FILE_WEEKLY]
            weeklyEnable = weeklyConf[CrawlerConstants.CONFIG_FILE_ENABLE]
            if weeklyEnable.strip().lower()=='true':
                dayOfWeek = [CrawlerManager.DAYOFWEEK[x] for x in weeklyConf[CrawlerConstants.CONFIG_FILE_DAYOFWEEK]]
                while(nextPossible.weekday() not in dayOfWeek):
                    nextPossible = nextPossible + datetime.timedelta(1)
        return time.mktime(nextPossible.timetuple())-time.time(), nextPossible
        
    def start(self):
        super(CrawlerManager, self).start()
        CTPUtils.Singleton = CTPUtils()
        CTPUtils.Singleton.start()
        self.__configAudit.start()
        self.__startTime = time.time()
        self.__startWorkers(0, self._numThread, True)
        waitTime, nextRunTime = self.__getDeltaBeforeNextRun()
        if waitTime>0:
            (days, hours, minutes, seconds) = getTimeDelta(nextRunTime)
            self.logger.info('Next Run would be scheduled after %d days %d hours %d minutes %d seconds @ %s', days, hours, minutes, seconds, nextRunTime.strftime('%Y-%m-%d %H:%M:%S'))
            self.__recurrenceAudit = Audit(self, waitTime, CrawlerConstants.VAL_AUDIT_PARAMETER_RECURRENCE, True)
            self.__recurrenceAudit.start()
        else:
            self.__startTask()
    
    def __startTask(self):
        self.__round+=1
        if self._noDb is False:
            self._startDbProxy()    
        
        if self.__failureHandling is False:
            self._initTask()
        else:
            self._getFailureTasks()
        self.logger.info('Round %d started with %d tasks initialized', self.__round, len(self._taskList))
        for i in range(0,self._numThread):
            if self.__workers[i].isBusy() is False:
                time.sleep(1)
                self._sendTask(i)

    def _startDbProxy(self, selfOnly=False):
        self.logger.debug('Start DB proxy')
        if self.dbProxy is not None:
            self.dbProxy.shutDown()
        self.dbProxy = MySqlProxy(self._dbHost, self._dbPort, self._dbUser, self._dbPasswd, self._dbName, logger=self.logger)
        self.dbProxy.start()
        if selfOnly:
            return
        for i in range(0,self._numThread):
            if self.__workers[i].dbProxy is not None:
                self.__workers[i].dbProxy.shutDown()
            self.__workers[i].dbProxy = MySqlProxy(self._dbHost, self._dbPort, self._dbUser, self._dbPasswd, self._dbName, logger=self.logger)
            self.__workers[i].dbProxy.start()
    
    def _stopDbProxy(self):
        self.logger.debug('Stop DB proxy')
        if self.dbProxy is not None:
            self.dbProxy.shutDown()
        self.dbProxy = None
        for i in range(0,self._numThread):
            if self.__workers[i].dbProxy is not None:
                self.__workers[i].dbProxy.shutDown()
                self.__workers[i].dbProxy = None
        
    def __startWorkers(self, begin, end, isInit=False):
        for i in range(begin, end):
            dbProxy = None
            worker = CrawlerWorker(self, i, dbProxy, self.logger)
            self.__workers[i] = worker
            worker.start()
            self.logger.info('Start worker %d', i)
                
    def _shutDown(self):
        CTPUtils.Singleton.shutDown()
        if self.dbProxy is not None:
            self.dbProxy.shutDown()
        if self.__recurrenceAudit is not None:
            self.__recurrenceAudit.shutDown()
        self.__configAudit.shutDown()
        self.__shutDownWorkers()
        super(CrawlerManager, self)._shutDown()
        
    def __shutDownWorkers(self):
        for i in self.__workers.keys():
            self.__workers[i].shutDown()
            self.logger.info('Shutdown worker %d', i)

    def _handleRequest(self, request):
        if super(CrawlerManager, self)._handleRequest(request):
            return True
        action = request[CrawlerConstants.PARA_ACTION]
        if cmp(action, CrawlerConstants.VAL_ACTION_AUDIT)==0:
            self.__handleAudit(request)
        elif cmp(action, CrawlerConstants.VAL_ACTION_NOTIFYDONE)==0:
            self._handleNotifyDone(request)
        elif cmp(action, CrawlerConstants.VAL_ACTION_NOTIFYPARTIAL) ==0:
            OneTimeThread(self._handleNotifyPartial, {'request':request}).start()
        else:
            self.logger.error('Unknown request')
            return False
        return True
    def __handleAudit(self, request):
        parameter = request[CrawlerConstants.PARA_AUDIT_PARAMETER]
        if parameter == CrawlerConstants.VAL_AUDIT_PARAMETER_CONFIG:
            self.__handleConfigAudit(request)        
        elif parameter == CrawlerConstants.VAL_AUDIT_PARAMETER_RECURRENCE:
            self.__handleRecurrenceAudit(request)
        else:
            self.logger.error('Unknown audit parameter')
    
    def __handleRecurrenceAudit(self, request):
        self.__failureHandlingFlag = False
        self.__totalTasks = 0
        self.__maxTime = 0
        self.__startTime = time.time()
        self.__startTask()
        waitTime, nextRunTime = self.__getDeltaBeforeNextRun()
        if waitTime>0:
            (days, hours, minutes, seconds) = getTimeDelta(nextRunTime)
            self.logger.info('Next Run would be scheduled after %d days %d hours %d minutes %d seconds @ %s', days, hours, minutes, seconds, nextRunTime.strftime('%Y-%m-%d %H:%M:%S'))
            self.__recurrenceAudit = Audit(self, waitTime, CrawlerConstants.VAL_AUDIT_PARAMETER_RECURRENCE, True)
            self.__recurrenceAudit.start()

    def __handleConfigAudit(self, request):
        self.__readConfig()
        self.__getCommonConfig()
        self._getNonCommonConfig(self.__config)
        self._validate()
        if self.__isValid is False:
            return
        for identifier in self.__workers.keys():
            self.__workers[identifier].changeSleepRange(self.__sleepRange)        
        if self._numThread>len(self.__workers):
            self.__startWorkers(len(self.__workers), self._numThread)
    
    def _validate(self):
        self.__isValid = True
        if len(self.__sleepRange)!=2:
            self.logger.error('sleepRange is not correct')
            self.__isValid = False
        try:
            if float(self.__sleepRange[1])<=float(self.__sleepRange[0]):
                self.logger.error('sleepRange is not correct')
                self.__isValid = False
        except:
            self.logger.error('sleepRange format is not float')
            self.__isValid = False
    
    def _handleNotifyDone(self, request):
        self.__totalTasks+=1
        rate = (time.time() - self.__startTime)/self.__totalTasks
        if request[CrawlerConstants.PARA_TOTAL_TIME] > self.__maxTime:
            self.__maxTime = request[CrawlerConstants.PARA_TOTAL_TIME]
        self.logger.info('Receive done:%s',request)
        self.logger.info('Average Rate:%f seconds/task. Current Rate: %f.Total Finished:%d', round(rate,2), request[CrawlerConstants.PARA_TOTAL_TIME], self.__totalTasks)
        if len(self.__workers)>self._numThread:
            self.__workers[request[CrawlerConstants.PARA_CRAWLER_ID]].shutDown()
            self.logger.info('Shutdown worker %d as workers num %d is bigger than thread num %d', request[CrawlerConstants.PARA_CRAWLER_ID], len(self.__workers), self._numThread)
            del self.__workers[request[CrawlerConstants.PARA_CRAWLER_ID]] 
            return
        retVal =self._sendTask(request[CrawlerConstants.PARA_CRAWLER_ID])
        if retVal is False:
            if self._isFinish():
                self._stopDbProxy()
                self.logger.info('DONE FOR CURRENT ROUND %d (start @ %s)', self.__round, datetime.datetime.fromtimestamp(self.__startTime).strftime('%Y-%m-%d %H:%M:%S'))
    
    def _isFinish(self):
        for worker in self.__workers.values():
            if worker.isBusy():
                return False
        
        return True
    def _sendTask(self, i):
        if self.__isValid is False:
            self.logger.error('Not valid')
            return False
        if i not in self.__workers:
            self.logger.error('No worker %d ', i)
            return False
        task = dict()
        taskAvailable = self._generateTask(task)
        if taskAvailable is False and self.__failureHandlingFlag is False:
            self._getFailureTasks()
            self.__failureHandlingFlag = True
            taskAvailable = self._generateTask(task, True)
        
        if taskAvailable:
            self.logger.info('Send task:%s to worker %d', task, i)
            self.__workers[i].addRequest(task)
        return taskAvailable
        
    def _generateTask(self, task, checkTaskList=True):
        if checkTaskList and len(self._taskList)==0:
            return False
        task[CrawlerConstants.CONFIG_FILE_SLEEP_RANGE] = self.__sleepRange
        task[CrawlerConstants.CONFIG_FILE_FAILURE_TABLENAME] = self.__failureTableName
        task[CrawlerConstants.PARA_ACTION] = CrawlerConstants.VAL_ACTION_CRAWL
        task[CrawlerConstants.CONFIG_FILE_DEBUG] = self.debug
        return True
            
    def _getNonCommonConfig(self, config):
        pass            
    def _handleNotifyPartial(self, request):
        pass
    
    def _initTask(self):
        pass
    
    def _getFailureTasks(self):
        if self.__failureUrlPattern is None:
            return
        sql = 'SELECT url from %s WHERE status>0 AND status<3 AND url like "%%%s%%"' % (self.__failureTableName, self.__failureUrlPattern)
        if self.dbProxy.execute(sql)>0:
            self._taskList.extend( [x[0] for x in self.dbProxy.cur.fetchall()])
        
class CrawlerWorker(RequestHandler):
    def __init__(self, controller, identifier, dbProxy, logger):
        super(CrawlerWorker, self).__init__(sleep_time=1)
        self.__controller = controller
        self.__identifier = identifier
        self.dbProxy = dbProxy
        self.__displayPrefix = '[WORKER%s]' % str(self.__identifier)
        self.__currentRequest = None
        self.__currentCrawler = None
        self.__sleep_range = [0.5,1]
        self.logger = logger
        self.__isBusy = False        
    
    def isBusy(self):
        return self.__isBusy
    
    def changeSleepRange(self, sleep_range):
        self.__sleep_range = sleep_range

    def getDisplayPrefix(self):
        return self.__displayPrefix

    def start(self):
        super(CrawlerWorker, self).start()
    
    def _shutDown(self):
        if self.__currentCrawler is not None:
            self.__currentCrawler.shutDown()
        super(CrawlerWorker, self)._shutDown()
        time.sleep(2)
    
    def addRequest(self, request, priority=0):
        action = request[CrawlerConstants.PARA_ACTION]
        if cmp(action, CrawlerConstants.VAL_ACTION_CRAWL)==0:
            self.__isBusy = True
        RequestHandler.addRequest(self, request, priority=priority)
    
    def _handleRequest(self, request):
        self.logger.debug('_handleRequest:%s', request)
        if super(CrawlerWorker, self)._handleRequest(request) is True:
            return True
        action = request[CrawlerConstants.PARA_ACTION]
        if cmp(action, CrawlerConstants.VAL_ACTION_CRAWL)==0:
            self.__crawl(request)
            return True
        return False
    
    def __crawl(self, request):
        self.logger.debug('start to crawl')
        if self.__currentCrawler is not None:
            self.addRequest(request)
            return
        try:            
            className = request[CrawlerConstants.PARA_CLASS]
            self.__currentRequest = request
            self.__sleep_range = request[CrawlerConstants.CONFIG_FILE_SLEEP_RANGE]
            self.__currentCrawler = className(self, self.dbProxy, request)
            self.__isBusy = True
            self.__currentCrawler.start()
        except Exception:
            traceInfo = traceback.format_exc()
            self.logger.error('Fail to init Crawler:%s ', traceInfo)
            className = None
        if className is None:
            result = {CrawlerConstants.PARA_STATUS:CrawlerConstants.VAL_STATUS_FAILURE, CrawlerConstants.PARA_TOTAL_TIME:0}
            self.notifyDone(result)
    
    def notifyDone(self, result):
        if self.__currentCrawler is not None:
            self.__currentCrawler.shutDown()
        request = dict()
        request.update(self.__currentRequest)
        request.update(result)
        request[CrawlerConstants.PARA_ACTION]=CrawlerConstants.VAL_ACTION_NOTIFYDONE
        request[CrawlerConstants.PARA_CRAWLER_ID]  = self.__identifier
        self.__currentCrawler = None
        self.__isBusy = False
        self.__currentRequest = None
        
        self.__controller.addRequest(request)
        
    
    def notifyPartial(self, result):
        request = dict()
        request.update(self.__currentRequest)
        request.update(result)
        request[CrawlerConstants.PARA_ACTION]=CrawlerConstants.VAL_ACTION_NOTIFYPARTIAL
        request[CrawlerConstants.PARA_CRAWLER_ID]  = self.__identifier
        
        self.__controller.addRequest(request)
    
    def randomSleep(self):
        sleepTime =self.__sleep_range[0] + (self.__sleep_range[1]-self.__sleep_range[0])*random.random()
        time.sleep(sleepTime)

class CrawlerBase(StoppableThread):
    def __init__(self, controller, dbProxy, request):
        super(CrawlerBase, self).__init__(1)
        self.controller = controller
        self.dbProxy = dbProxy
        self.failureTableName = request[CrawlerConstants.CONFIG_FILE_FAILURE_TABLENAME]
        self.debug = request[CrawlerConstants.CONFIG_FILE_DEBUG]
        self.totalNum = 0
        self.totalPage = 0
        self.totalSuccessPage = 0
        self.logger = Logging.LOGGER

    def run(self):
        self.__startTime = time.time()
        self.controller.randomSleep()
    
    def _fetchContent(self, url, data=None, record=True):
        try:
            self.totalPage+=1
            (content, warning) = CrawlerCommon.readContent(url, data=data)
            self.totalSuccessPage+=1
            return content
        except:
            self.logger.error('Fail to fetch content for url:%s', url)
            if record:
                self._recordFailure(url, 'Fail to fetch content')
            return None

    def _recordFailure(self, url, reason):
        if self.dbProxy is None:
            return
        sql = 'SELECT status from %s where url="%s"' % (self.failureTableName, url)
        count = self.dbProxy.execute(sql)
        #count = self.dbProxy.cur.fetchone()[0]
        if count>0:
            status = self.dbProxy.cur.fetchone()[0]
            if status>=0:
                sql = 'UPDATE %s SET status=status+1, reason="%s" where url="%s"' % (self.failureTableName, reason, url)
            else:
                sql = 'UPDATE %s SET status=1, reason="%s" where url="%s"' % (self.failureTableName, reason, url)
        else:
            sql = 'INSERT INTO %s (url,reason) values ("%s","%s")' % (self.failureTableName, url, reason)
        
        if self.dbProxy.execute(sql)>0:
            self.dbProxy.commit()
    
    def _recoverFailure(self, url):
        if self.dbProxy is None:
            return
        sql = 'SELECT count(*) from %s where url="%s" and status>0' % (self.failureTableName, url)
        self.dbProxy.execute(sql)
        count = self.dbProxy.cur.fetchone()[0]
        if count>0:
            sql = 'UPDATE %s SET status=0-status where url="%s" and status>0' %(self.failureTableName, url)
            if self.dbProxy.execute(sql)>0:
                self.dbProxy.commit()
        
    def _writeTable(self, sql):
        if self.dbProxy is None:
            return 0
        count = self.dbProxy.execute(sql)
        if count>0:
            self.dbProxy.commit()
        return count
            
    def _reportDone(self, status, para=None):
        result = {CrawlerConstants.PARA_STATUS:status,
                  CrawlerConstants.PARA_TOTAL_TIME:time.time()-self.__startTime, 
                  CrawlerConstants.PARA_TOTAL_NUM:self.totalNum}
        if para is not None:
            result.update(para)
        OneTimeThread(self.controller.notifyDone, {'result':result}).start()

def getTimeDelta(nextTime):
    n = datetime.datetime.now()
    timedelta = nextTime - n
    days = timedelta.days
    seconds = timedelta.seconds
    hours = seconds/60/60
    minutes = (seconds - hours*60*60)/60
    seconds = seconds - hours*60*60 - minutes*60
    return (days, hours, minutes, seconds)