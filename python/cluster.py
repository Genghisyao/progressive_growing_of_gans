# -*- coding:utf-8 -*-
import json
import re
import time
import string
import jieba.analyse
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans
from db_init import *


class ClusterController():
    """
    聚类算法
    """
    def __init__(self):
        self.t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def getAllData(self, n):
        resultList = []
        sql_query1 = """
                    SELECT id, Ttitle, site, Tpublish_datetime
                    FROM news_text
                    WHERE TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= %d
                    GROUP BY Ttitle, site
                """ % n
        query1 = session.execute(sql_query1)
        for q in query1:
            Tid = q['id']
            title = q['Ttitle']
            channel = q['site']
            channeltype = 'news'
            resultList.append([Tid, title, channeltype])

        sql_query2 = """
                    SELECT id, Ttitle, Tpublish_datetime
                    FROM tieba_text
                    WHERE TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= %d
                    GROUP BY Ttitle
                """ % n
        query2 = session.execute(sql_query2)
        for q in query2:
            Tid = q['id']
            title = q['Ttitle']
            channel = 'tieba.baidu.com'
            channeltype = 'tieba'
            resultList.append([Tid, title, channeltype])

        sql_query3 = """
                    SELECT id, Ttitle, Tpublish_datetime
                    FROM luntan_text
                    WHERE TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= %d
                    GROUP BY Ttitle
                """ % n
        query3 = session.execute(sql_query3)
        for q in query3:
            Tid = q['id']
            title = q['Ttitle']
            channel = 'bbs.tianya.cn'
            channeltype = 'luntan'
            resultList.append([Tid, title, channeltype])

        sql_query4 = """
                    SELECT id, mid, Ttitle, Tpublish_datetime
                    FROM (SELECT * FROM zhihu_text ORDER BY Tpublish_datetime) a
                    WHERE TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= %d
                    GROUP BY Ttitle
                """ % n
        query4 = session.execute(sql_query4)
        for q in query4:
            Tid = q['id'] + ';' + q['mid']
            title = q['Ttitle']
            channel = 'zhihu.com'
            channeltype = 'zhihu'
            resultList.append([Tid, title, channeltype])

        sql_query5 = """
                    SELECT mid, LEFT(content, 30) AS Ttitle, publish_datetime
                    FROM t_sinablog
                    WHERE TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= %d
                    GROUP BY Ttitle
                """ % n
        query5 = session.execute(sql_query5)
        for q in query5:
            Tid = q['mid']
            title = q['Ttitle']
            channel = 'weibo.com'
            channeltype = 'weibo'
            resultList.append([Tid, title, channeltype])

        sql_query6 = """
                    SELECT pid, wid, title, publish_datetime
                    FROM t_weixin
                    WHERE TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= %d
                    GROUP BY title
                """ % n
        query6 = session.execute(sql_query6)
        for q in query6:
            Tid = q['pid'] + ';' + q['wid']
            title = q['title']
            channel = 'weixin.com'
            channeltype = 'weixin'
            resultList.append([Tid, title, channeltype])
        return resultList

    def do(self):
        n = 1
        resultList = self.getAllData(n)
        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        stopWords = ['...', 'via', 'video', '#', u'中山大学', u'中大', u'视频', u'校园', u'学校', u'大学', u'校园', u'广州',
                     u'深圳', u'中山', u'发表了博文', u'学院', u'学园', u'校区', u'学生', u'师生', u'如何', u'评价', u'链接',
                     u'网页', u'原标题']
        corpus = list()
        for item in resultList:
            x = item[1]
            for w in stopWords:
                x = x.replace(w, '').strip()
            # zh_punctuation = u'~·！@#￥%……&*（）——【】、；：‘’“”《》？，。|'
            x = re.sub(r'[' + string.printable + ']', '', x)  # 去除数字、英文、英文标点
            corpus.append(x)
        tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))  # 训练
        word = vectorizer.get_feature_names()  # 特征词列表
        weight = tfidf.toarray()
        clf = KMeans(n_clusters=20)  # 聚类
        clf.fit(weight)
        sampleDict = dict()
        for x in clf.labels_:
            # 统计每个类有多少篇文章
            if x not in sampleDict:
                sampleDict[x] = 1
            else:
                sampleDict[x] += 1
        total_cnt = len(resultList)
        large_threshold = 0.1
        medium_threshold = 0.125
        largeSamples = list()
        mediumSamples = list()
        mediumSize = 0
        for key in sampleDict:
            print key, sampleDict[key]
            if sampleDict[key] * 1.0 / total_cnt > large_threshold:
                largeSamples.append(key)
            else:
                mediumSize += sampleDict[key]
        for key in sampleDict:
            if key in largeSamples:
                continue
            if sampleDict[key] * 1.0 / mediumSize > medium_threshold:
                mediumSamples.append(key)
        print largeSamples
        print mediumSamples
        dataList = []
        if largeSamples:
            for l in largeSamples:
                indexs = np.argwhere(clf.labels_== l)  # 取出对应下标
                titleList = []
                keywordList = []
                valueList = []
                for index in indexs:
                    i = int(index)
                    Tid = resultList[i][0]
                    title = resultList[i][1].strip()
                    channeltype = resultList[i][2]
                    # print title
                    for w in stopWords:
                        title = title.replace(w, '')  # 去除停用词
                    # zh_punctuation = u'~·！@#￥%……&*（）——【】、；：‘’“”《》？，。|'
                    title = re.sub(r'[' + string.printable + ']', '', title)  # 去除数字、英文、英文标点
                    titleList.append(title)
                    valueList.append({"Tid":Tid, "channeltype":channeltype})
                longcontent = '\n'.join(titleList)  # 将标题拼接成长文本
                tags = jieba.analyse.extract_tags(longcontent, topK=10, withWeight=True)  # 分析长文本，获取关键词
                for t in tags:
                    keyword = t[0]  # 关键词
                    keywordList.append(keyword)
                cid = l  # 聚类id
                size = 'large'  # 聚类大小
                quantity = sampleDict[cid]  # 文章数
                add_datetime = self.t
                keywords = ','.join(keywordList)  # 关键词
                value_list = json.dumps(valueList)  # 【Tid，channeltype】列表
                dataList.append([cid, size, quantity, add_datetime, keywords, value_list])

        if mediumSamples:
            for m in mediumSamples:
                indexs = np.argwhere(clf.labels_== m)  # 取出对应下标
                titleList = []
                keywordList = []
                valueList = []
                for index in indexs:
                    i = int(index)
                    Tid = resultList[i][0]
                    title = resultList[i][1].strip()
                    channeltype = resultList[i][2]
                    # print title
                    for w in stopWords:
                        title = title.replace(w, '')  # 去除停用词
                    # zh_punctuation = u'~·！@#￥%……&*（）——【】、；：‘’“”《》？，。|'
                    title = re.sub(r'[' + string.printable + ']', '', title)  # 去除数字、英文、英文标点
                    titleList.append(title)
                    valueList.append({"Tid":Tid, "channeltype":channeltype})
                longcontent = '\n'.join(titleList)  # 将标题拼接成长文本
                keywords = jieba.analyse.extract_tags(longcontent, topK=10, withWeight=True)  # 分析长文本，获取关键词
                for k in keywords:
                    keyword = k[0]  # 关键词
                    keywordList.append(keyword)
                cid = m
                size = 'medium'
                quantity = sampleDict[cid]  # 文章数
                add_datetime = self.t
                keywords = ','.join(keywordList)
                value_list = json.dumps(valueList)
                dataList.append([cid, size, quantity, add_datetime, keywords, value_list])
        self.insert(dataList)

    def insert(self, dataList):
        valueList = []
        for q in dataList:
            valueList.append(
                " ('%s','%s','%s','%s','%s','%s') " % (q[0], q[1], q[2], q[3], q[4], q[5]))
        sql = "INSERT INTO text_cluster (cid, `size`, quantity, add_datetime, keywords, value_list) VALUES "
        sql_size = 500
        if len(valueList) > 0:
            index = 0
            while index < len(valueList):
                # print index, min(index + sql_size, len(valueList)) - 1
                sql_insert = sql + ','.join(valueList[index: min(index + sql_size, len(valueList))])
                session.execute(sql_insert)
                session.commit()
                index += sql_size

if __name__ == '__main__':
    print '_____start_____'
    ClusterController().do()
