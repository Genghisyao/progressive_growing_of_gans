# -*- coding:utf-8 -*-
import xmlrpclib




if __name__ == '__main__':
    print "_______start_______"
    server = xmlrpclib.ServerProxy('http://localhost:5060')
    ret = server.hello('LHB')
    print ret
    # ret = server.downloadEventReport(2)