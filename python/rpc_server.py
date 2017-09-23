# -*- coding:utf-8 -*-
from utils import *
from report import *

class RPCHandler(RequestHandler):
    def __init__(self, serverIp, serverPort, serviceHandler=None, rpcFuncInstance=None, sleep_time=0.1, logger=None):
        super(RPCHandler, self).__init__(sleep_time)
        self.__serverIp = serverIp
        self.__serverPort = serverPort
        
        #service handler is the handler instance to actually handle the request
        #it is the application level
        self._serviceHandler = serviceHandler
        
        #rpcFuncInstance is the rpc class instance to route income request
        if rpcFuncInstance is None: 
            self.__rpcFuncInstance = RPCFuncBase(self)
        else:
            self.__rpcFuncInstance = rpcFuncInstance
        
        #rpcClient is the rpc client to send request out
        self.rpcClient = None
        self.identifier = 'http://%s:%d' % (serverIp, serverPort)
        if logger is not None:
            self.logger = logger

    def setRPCClient(self, rpcClient):
        self.rpcClient = rpcClient

    def setRpcFuncInstance(self, rpcFuncInstance):
        self.__rpcFuncInstance = rpcFuncInstance
    
    def setServiceHandler(self, serviceHandler):
        self._serviceHandler = serviceHandler

    def sendServiceRequest(self, funcName, paraList, credential):
        if self.rpcClient is None:
            self.logger.error('rpc client is not set')
            return
        self.rpcClient.service(funcName, paraList, credential)
                        
    def start(self):
        super(RPCHandler, self).start()
        self.__startRPCServer()
        
    def __startRPCServer(self):    
        self.__rpcServer = RPCServer(self.__serverIp, self.__serverPort, self.__rpcFuncInstance, self.logger)
        self.__rpcServer.start()

    def _shutDown(self):
        '''
        Shutdown the agent, including all its threads and tasks
        '''
        #stop RPCServer
        if self.__rpcServer is not None:
            self.logger.info('Shutting down the RPC server')
            self.__rpcServer.shutDownServer()

        #stop jobs
        self._stopTasks()
        
        #stop the thread itself
        super(RPCHandler, self)._shutDown()
    
        
    def _handleRequest(self, request):
        if not 'action' in request:
            self.logger.error('Invalid request that does not contain action element')
            return
        action = request['action']
        
        if cmp(action, 'shutdown')==0:
            self._shutDown()            
        elif cmp(action, 'service')==0:
            self._handleServiceReq(request)
        else:
            self.logger.error('Unknown action request:%s', action)
        
    def _handleServiceReq(self, request):
        if isinstance(self._serviceHandler,RequestHandler):
            self._serviceHandler.addRequest(request)
        else:
            func = request['funcName']
            paraList = request['paraList']
            credential = request['credential']
            mtd = getattr(self._serviceHandler, func)
            mtd(paraList, credential)
            
    def _stopTasks(self):
        '''
        gracefully wait until the requests in request handler are handled
         
        '''
        pass
    
    def peerStop(self, credential):
        self.logger.error('peerStop shall be implemented by sub-class')
        pass

class RPCFuncBase(object):
    def __init__(self, server):
        self._server = server
                
    def _buildServiceDict(self):
        request = dict()
        request['action']='service'
        return request
    
    def peerStop(self, credential):
        self._server.peerStop(credential)
        return True
        
    def heartbeat(self):
        return True
    
    def service(self, funcName, paraList, credential):
        request = self._buildServiceDict()
        request['funcName'] = funcName
        request['paraList'] = paraList
        request['credential'] = credential
        self._server.addRequest(request)
        return True

class TradeServerRPCFunc(RPCFuncBase):
    def __init__(self, controller):
        super(TradeServerRPCFunc, self).__init__(controller)

    def myfunc(self, para1, para2):
        return self._server.myfunc(para1, para2)

    def hello(self, name):
        return self._server.hello(name)

    def downloadEventReport(self, event_id):
        return self._server.downloadEventReport(event_id)

class XMLRPCTradeServer(RPCHandler):
    def __init__(self, json_config_file, orderHandler=None):
        self.__config = self.__readConfig(json_config_file)
        self.__itradeDict = dict()
        server_ip = self.__config[CONF_FILE_ITRADE_SERVER_IP]
        server_port =  self.__config[CONF_FILE_ITRADE_SERVER_PORT]
        super(XMLRPCTradeServer, self).__init__(server_ip,server_port, None, TradeServerRPCFunc(self), 0.001)
        self.logger = Logging.getLogger(Logging.LOGGER_NAME_ITRADE)
            
    def __readConfig(self, json_config_file):
        className = self.__class__.__name__
        rindex = className.rfind('.')
        if rindex >= 0:
            className = className[rindex+1:]
        c = Configuration(json_config_file)
        return c.readConfig()[className]
        
    def start(self):
        super(XMLRPCTradeServer, self).start()
    
    def _shutDown(self):

        super(XMLRPCTradeServer, self)._shutDown()
        
    def myfunc(self, para1, para2):
        return 'OK'

    def hello(self, name):
        word = 'Hello, %s' % name
        return word

    def downloadEventReport(self, event_id):
        import time
        start = time.time()
        onlyEventReport().Controller(event_id)
        end = time.time()
        # print 'Complete the event report in %.4f seconds' % (end - start)
        return 'Complete the event report in %.4f seconds' % (end - start)


if __name__ == '__main__':
    print u"——————————start——————————"
    CONF_FILE_ITRADE_SERVER_IP = 'ip'
    CONF_FILE_ITRADE_SERVER_PORT = 'port'
    root_path = os.getcwd()  # 根目录
    conf_path = root_path + '/conf'  # 配置目录
    # print conf_path
    rpc = XMLRPCTradeServer(conf_path + "//" + "server.conf")
    rpc.start()

