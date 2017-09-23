# -*- coding:utf-8 -*-
from sqlalchemy import Column, String, Float, Text, DateTime, Integer
from sqlalchemy.sql import text
from sqlalchemy import and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# 创建对象的基类:
Base = declarative_base()

class EventList(Base):
    """
    数据库表————事件列表
    """
    __tablename__ = 'event_list'
    event_id = Column(String(150), primary_key=True)
    event_name = Column(String(255))
    add_datetime = Column(DateTime)
    keywords = Column(String(255))
    non_keywords = Column(String(255))

class LuntanTie(Base):
    """
    数据库表————论坛帖子
    """
    __tablename__ = 'luntan_text'
    id = Column(String(150), primary_key=True)
    Ttitle = Column(String(250))
    add_datetime = Column(DateTime)
    Tpublish_datetime = Column(DateTime)
    Tauthor_id = Column(String(100))
    Tauthor_name = Column(String(100))
    Tread = Column(Integer)
    Treply = Column(Integer)
    Tcontent = Column(Text)

    def __init__(self,id,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tread,Treply,Tcontent):
        self.id = id
        self.Ttitle = Ttitle
        self.add_datetime = add_datetime
        self.Tpublish_datetime = Tpublish_datetime
        self.Tauthor_id = Tauthor_id
        self.Tauthor_name = Tauthor_name
        self.Tread = Tread
        self.Treply = Treply
        self.Tcontent = Tcontent

    def __repr__(self):
        return "<LuntanTie('%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.id,self.Ttitle,self.add_datetime,self.Tpublish_datetime,self.Tauthor_id,self.Tauthor_name,self.Tread,self.Treply,self.Tcontent)

class LuntanComment(Base):
    """
    数据库表————论坛评论
    """
    __tablename__ = 'luntan_comment'
    id = Column(String(150), primary_key=True)
    Ctime = Column(DateTime, primary_key=True)
    Cid = Column(String(100))
    Cip = Column(String(100))
    Cname = Column(String(100))
    Ctext = Column(Text)
    Creplyuserid = Column(String(100))

    def __init__(self,id,Ctime,Cid,Cip,Cname,Ctext,Creplyuserid):
        self.id = id
        self.Ctime = Ctime
        self.Cid = Cid
        self.Cip = Cip
        self.Cname = Cname
        self.Ctext = Ctext
        self.Creplyuserid = Creplyuserid

    def __repr__(self):
        return "<LuntanComment('%s','%s','%s','%s','%s','%s','%s')>" % (self.id,self.Ctime,self.Cid,self.Cip,self.Cname,self.Ctext,self.Creplyuserid)

class TiebaText(Base):
    """
    数据库表————百度贴吧
    """
    __tablename__ = 'tieba_text'
    id = Column(String(150), primary_key=True)
    Ttitle = Column(String(250))
    add_datetime = Column(DateTime)
    Tpublish_datetime = Column(DateTime)
    Tauthor_id = Column(String(100))
    Tauthor_name = Column(String(100))
    Treply = Column(Integer)
    Tcontent = Column(Text)

    def __init__(self,id,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Treply,Tcontent):
        self.id = id
        self.Ttitle = Ttitle
        self.add_datetime = add_datetime
        self.Tpublish_datetime = Tpublish_datetime
        self.Tauthor_id = Tauthor_id
        self.Tauthor_name = Tauthor_name
        self.Treply = Treply
        self.Tcontent = Tcontent

    def __repr__(self):
        return "<TiebaText('%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.id,self.Ttitle,self.add_datetime,self.Tpublish_datetime,self.Tauthor_id,self.Tauthor_name,self.Treply,self.Tcontent)

class TiebaComment(Base):
    """
    数据库表————百度贴吧评论
    """
    __tablename__ = 'tieba_comment'
    id = Column(String(150), primary_key=True)
    Ctime = Column(DateTime, primary_key=True)
    Cid = Column(String(100))
    Cname = Column(String(100))
    Ctext = Column(Text)
    Creplyuserid = Column(String(100))

    def __init__(self,id,Ctime,Cid,Cname,Ctext,Creplyuserid):
        self.id = id
        self.Ctime = Ctime
        self.Cid = Cid
        self.Cname = Cname
        self.Ctext = Ctext
        self.Creplyuserid = Creplyuserid

    def __repr__(self):
        return "<TiebaComment('%s','%s','%s','%s','%s','%s')>" % (self.id,self.Ctime,self.Cid,self.Cname,self.Ctext,self.Creplyuserid)

class NewsText(Base):
    """
    数据库表————新闻正文
    """
    __tablename__ = 'news_text'
    id = Column(String(150), primary_key=True)
    site = Column(String(150))
    Ttitle = Column(String(250))
    add_datetime = Column(DateTime)
    Tpublish_datetime = Column(DateTime)
    Tauthor_name = Column(String(100))
    Treply = Column(Integer)
    Tcontent = Column(Text)

    def __init__(self,id,site,Ttitle,add_datetime,Tpublish_datetime,Tauthor_name,Treply,Tcontent):
        self.id = id
        self.site = site
        self.Ttitle = Ttitle
        self.add_datetime = add_datetime
        self.Tpublish_datetime = Tpublish_datetime
        self.Tauthor_name = Tauthor_name
        self.Treply = Treply
        self.Tcontent = Tcontent

    def __repr__(self):
        return "<NewsText('%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.id,self.site,self.Ttitle,self.add_datetime,self.Tpublish_datetime,self.Tauthor_name,self.Treply,self.Tcontent)

class NewsComment(Base):
    """
    数据库表————新闻评论
    """
    __tablename__ = 'news_comment'
    id = Column(String(150), primary_key=True)
    site = Column(String(150))
    Ctime = Column(DateTime, primary_key=True)
    Cid = Column(String(100), primary_key=True)
    Cip = Column(String(100))
    Cname = Column(String(250))
    Ctext = Column(Text)
    Creplyuserid = Column(String(100))

    def __init__(self,id,site,Ctime,Cid,Cip,Cname,Ctext,Creplyuserid):
        self.id = id
        self.site = site
        self.Ctime = Ctime
        self.Cid = Cid
        self.Cip = Cip
        self.Cname = Cname
        self.Ctext = Ctext
        self.Creplyuserid = Creplyuserid

    def __repr__(self):
        return "<NewsComment('%s','%s','%s','%s','%s','%s','%s','%s')>" % (self.id,self.site,self.Ctime,self.Cid,self.Cip,self.Cname,self.Ctext,self.Creplyuserid)

class ZhihuText(Base):
    """
    数据库表————知乎正文
    """
    __tablename__ = 'zhihu_text'
    id = Column(String(150), primary_key=True)
    mid = Column(String(150), primary_key=True)
    Ttitle = Column(String(250), index=True)
    add_datetime = Column(DateTime, index=True)
    Tpublish_datetime = Column(DateTime, index=True)
    Tauthor_id = Column(String(250), index=True)
    Tauthor_name = Column(String(250), index=True)
    Tfans = Column(Integer, index=True)
    Tread = Column(Integer, index=True)
    Treply = Column(Integer, index=True)
    Tlike = Column(Integer, index=True)
    Tcontent = Column(Text)

    def __init__(self,id,mid,Ttitle,add_datetime,Tpublish_datetime,Tauthor_id,Tauthor_name,Tfans,Tread,Treply,Tlike,Tcontent):
        self.id = id
        self.mid = mid
        self.Ttitle = Ttitle
        self.add_datetime = add_datetime
        self.Tpublish_datetime = Tpublish_datetime
        self.Tauthor_id = Tauthor_id
        self.Tauthor_name = Tauthor_name
        self.Tfans = Tfans
        self.Tread = Tread
        self.Treply = Treply
        self.Tlike = Tlike
        self.Tcontent = Tcontent

    def __repr__(self):
        return "<ZhihuText('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" \
               % (self.id,self.mid,self.Ttitle,self.add_datetime,self.Tpublish_datetime,self.Tauthor_id,self.Tauthor_name,
                  self.Tfans,self.Tread,self.Treply,self.Tlike,self.Tcontent)

class TextSelect(Base):
    """
    数据库表————正文处理
    """
    __tablename__ = 'text_select'
    Tid = Column(String(150), primary_key=True)
    event_id = Column(Integer, primary_key=True)
    title = Column(String(250), index=True)
    add_datetime = Column(DateTime)
    publish_datetime = Column(DateTime)
    author_id = Column(String(150), index=True)
    author_name = Column(String(150), index=True)
    content = Column(Text)
    reply_count = Column(Integer, index=True)
    read_count = Column(Integer, index=True)
    like_count = Column(Integer, index=True)
    collect_count = Column(Integer, index=True)
    forward_count = Column(Integer, index=True)
    channeltype = Column(String(150), index=True)
    channel = Column(String(150), primary_key=True)
    correlation = Column(String(150), index=True)
    heatwords = Column(String(150), index=True)
    heat = Column(Float, index=True)

    def __init__(self,Tid,event_id,title,add_datetime,publish_datetime,author_id,author_name,content,reply_count,read_count,
                like_count,collect_count,forward_count,channeltype,channel,correlation,heatwords,heat):
        self.Tid = Tid
        self.event_id = event_id
        self.title = title
        self.add_datetime = add_datetime
        self.publish_datetime = publish_datetime
        self.author_id = author_id
        self.author_name = author_name
        self.content = content
        self.reply_count = reply_count
        self.read_count = read_count
        self.like_count = like_count
        self.collect_count = collect_count
        self.forward_count = forward_count
        self.channeltype = channeltype
        self.channel = channel
        self.correlation = correlation
        self.heatwords = heatwords
        self.heat = heat

    def __repr__(self):
        return "<TextSelect('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.Tid,self.event_id,self.title,self.add_datetime,self.publish_datetime,self.author_id,self.author_name,
                self.content,self.reply_count,self.read_count,self.like_count,self.collect_count,self.forward_count,
                self.channeltype,self.channel,self.correlation,self.heatwords,self.heat)

class TextGrowth(Base):
    """
    数据库表————正文评论、阅读、赞、转载量增量更新
    """
    __tablename__ = 'text_growth'
    Tid = Column(String(150), primary_key=True)
    event_id = Column(Integer, primary_key=True)
    crawl_datetime = Column(DateTime, primary_key=True)
    reply_count = Column(Integer, index=True)
    read_count = Column(Integer, index=True)
    like_count = Column(Integer, index=True)
    collect_count = Column(Integer, index=True)
    forward_count = Column(Integer, index=True)
    channeltype = Column(String(150), index=True)
    channel = Column(String(150), primary_key=True)
    heat = Column(Float, index=True)

    def __init__(self,Tid,event_id,crawl_datetime,reply_count,read_count,like_count,collect_count,forward_count,channeltype,channel,heat):
        self.Tid = Tid
        self.event_id = event_id
        self.crawl_datetime = crawl_datetime
        self.reply_count = reply_count
        self.read_count = read_count
        self.like_count = like_count
        self.collect_count = collect_count
        self.forward_count = forward_count
        self.channeltype = channeltype
        self.channel = channel
        self.heat = heat

    def __repr__(self):
        return "<TextGrowth('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.Tid,self.event_id,self.crawl_datetime,self.reply_count,self.read_count,self.like_count,self.collect_count,self.forward_count,self.channeltype,self.channel,self.heat)

class EventStatistics(Base):
    """
    数据库表————事件统计
    """
    __tablename__ = 'event_statistics'
    event_id = Column(String(150), primary_key=True)
    # keywords = Column(String(150), primary_key=True)
    crawl_datetime = Column(DateTime, primary_key=True)
    reply_total = Column(Integer, index=True)
    read_total = Column(Integer, index=True)
    like_total = Column(Integer, index=True)
    collect_total = Column(Integer, index=True)
    original_total = Column(Integer, index=True)
    forward_total = Column(Integer, index=True)
    event_heat = Column(Float, index=True)

    def __init__(self,event_id,crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total,event_heat):
        self.event_id = event_id
        self.crawl_datetime = crawl_datetime
        self.reply_total = reply_total
        self.read_total = read_total
        self.like_total = like_total
        self.collect_total = collect_total
        self.original_total = original_total
        self.forward_total = forward_total
        self.event_heat = event_heat

    def __repr__(self):
        return "<EventStatistics('%s','%s','%s','%s','%s','%s','%s','%s','%s')>" % \
               (self.event_id,self.crawl_datetime,self.reply_total,self.read_total,self.like_total,self.collect_total,
                self.original_total,self.forward_total,self.event_heat)

