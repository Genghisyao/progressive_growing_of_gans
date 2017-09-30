# -*- coding:utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# 导入数据库模型
from db_model import *

#数据库配置
DB_USER = 'root'
DB_PASSWORD = 'zzm15331411'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'sentiment'
DB_CHATSET = 'utf8mb4'

# 初始化数据库连接:
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' %
                       (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT,DB_NAME, DB_CHATSET), echo=False)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
session = DBSession()

def init_db():
    '''初始化数据库结构'''
    Base.metadata.create_all(engine)


def drop_db():
    '''清空数据库结构'''
    Base.metadata.drop_all(engine)

# 如果数据库不存在则初始化数据库结构
init_db()
