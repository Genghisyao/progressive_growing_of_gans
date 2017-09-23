'''
Created on 11 Apr 2017

@author: eyaomai
'''
import requests
import time
import random
class SessionCrawler(object):
    '''
    classdocs
    '''


    def __init__(self, session=None, sleepRange=[1,2], logger=None):
        '''
        Constructor
        '''
        if session is None:
            self.session = requests.session()
        else:
            self.session = session
        self.logger = logger
        self.sleepRange = sleepRange
        self.lastCrawlTime = 0
    
    def get(self, url, headers=None):
        #self.randomSleep()
        if headers is not None:
            result = self.session.get(url,headers=headers)
        else:
            result = self.session.get(url)
        self.lastCrawlTime = time.time()
        return result.text

    def randomSleep(self):
        if time.time() - self.lastCrawlTime < self.sleepRange[0]:
            sleepTime =self.sleepRange[0] + (self.sleepRange[1]-self.sleepRange[0])*random.random()            
            time.sleep(sleepTime)
    