# -*- coding:utf-8 -*-
from db_init import *
import time,re

class HotWarning():

    def __init__(self):
        # 获取热表中的数据
        sql_query = """
              SELECT Tid, title, content, reply_count, read_count,
              forward_count, heat FROM hot_article
              """
        query = session.execute(sql_query)
        hot_target = []
        for q in query:
            hot_target.append((q[0],q[1],q[2],q[3],q[4],q[5],q[6]))
        self.hot_target = hot_target


    #敏感词汇预警
    def word_warning(self):
        #h获取数据库中的敏感词汇
        sql = "SELECT * FROM sensitive_words"
        query = session.execute(sql)
        sen_mes = [] #敏感词汇信息
        sen_words = [] #敏感词汇
        for q in query:
            sen_mes.append((q[0], q[1]))

        hot_warning_mes = []
        for article_mes in self.hot_target:
            #warning_level = 0
            warning_level = ""
            warning_id = article_mes[0]
            warning_datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            warning_type = ""
            threshold_value = ""
            reason = ""
            warning_value = ""
            for single in sen_mes:
                word = single[1].split('|')
                for w in word:

                    #组合敏感词
                    if '&' in w:
                        com_word = w.split('&')
                        count = 0
                        final_word = ""
                        for single_word in com_word:
                            if single_word in article_mes[2]:
                                final_word += single_word + ' '
                                count += 1
                        if count == len(com_word):
                            if (str(single[0]) not in warning_level):
                                warning_level += str(single[0])
                            warning_type = "sensitive_words"
                            threshold_value = threshold_value + final_word + " "
                            reason = "文章中存在敏感词".decode('utf-8')
                            warning_value = warning_value + final_word + " "

                    #单个敏感词
                    elif w in article_mes[2]:
                        #warning_level = single[0]
                        if(str(single[0]) not in warning_level):
                            warning_level += str(single[0])
                        warning_type = "sensitive_words"
                        threshold_value = threshold_value + w + " "
                        reason = "文章中存在敏感词".decode('utf-8')
                        warning_value = warning_value + w + " "
            if (warning_level != ""):
                warning_tuple = (warning_id, warning_level, warning_datetime, warning_type, threshold_value, reason, warning_value)
                hot_warning_mes.append(warning_tuple)

        # 将预警文章数据导入的数据库
        sql = "INSERT INTO  hot_article_warning(Tid, level, warning_datetime, type, threshold_value, reason, data_value) VALUES"
        del_sql = "DELETE FROM hot_article_warning WHERE Tid in (%s) "
        if len(hot_warning_mes) > 0:
            insert_data = []
            del_id = []
            for q in hot_warning_mes:
                insert_data.append(" ('%s' ,'%s','%s','%s','%s','%s','%s') " % (q[0], q[1], q[2], q[3], q[4], q[5], q[6]))
                del_id.append("'" + q[0] + "'")

            sql_insert = sql + ','.join(insert_data)
            delete_sql = del_sql % ','.join(del_id)
            session.execute(delete_sql)
            session.execute(sql_insert)
            session.commit()



    ##指标预警
    def target_warning(self):

        #获取每个指标的预警阈值
        sql_query = "SELECT level ,threshold_reply ,threshold_read, threshold_forward, threshold_heat FROM hot_article_warning_threshold "
        query = session.execute(sql_query)

        hot_threshold = []
        for q in query:
            hot_threshold.append((q[0],q[1],q[2],q[3],q[4]))

        hot_warning_mes = []
        #将热表的数据与阈值表的数据进行比较
        for article_mes in self.hot_target:
            warning_level = 0
            warning_id = article_mes[0]
            warning_datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            warning_type = ""
            threshold_value = 0
            reason = ""
            warning_value = 0
            for warning_threshold in hot_threshold:
                if(article_mes[3] >= warning_threshold[1]):
                    warning_level = warning_threshold[0]
                    warning_type = "reply"
                    threshold_value = warning_threshold[1]
                    reason = "评论数量超过预警的阈值".decode('utf-8')
                    warning_value = article_mes[3]
                elif (article_mes[4] >= warning_threshold[2]):
                    warning_level = warning_threshold[0]
                    warning_type = "read"
                    threshold_value = warning_threshold[2]
                    reason = "阅读数量超过预警的阈值".decode('utf-8')
                    warning_value = article_mes[4]
                elif (article_mes[5] >= warning_threshold[3]):
                    warning_level = warning_threshold[0]
                    warning_type = "forward"
                    threshold_value = warning_threshold[3]
                    reason = "转发数量超过预警的阈值".decode('utf-8')
                    warning_value = article_mes[5]
                elif (article_mes[6] >= warning_threshold[4]):
                    warning_level = warning_threshold[0]
                    warning_type = "heat"
                    threshold_value = warning_threshold[4]
                    reason = "热度超过预警的阈值".decode('utf-8')
                    warning_value = article_mes[6]
                if(warning_level != 0):
                    warning_tuple = (warning_id, str(warning_level), warning_datetime, warning_type, threshold_value, reason, warning_value)
                    hot_warning_mes.append(warning_tuple)
                    break

        #将预警文章数据导入的数据库
        sql = "INSERT INTO  hot_article_warning(Tid, level, warning_datetime, type, threshold_value, reason, data_value) VALUES"
        del_sql = "DELETE FROM hot_article_warning WHERE Tid in (%s) "
        if len(hot_warning_mes) > 0:
            insert_data = []
            del_id = []
            for q in hot_warning_mes:
                insert_data.append(" ('%s' ,'%s','%s','%s','%s','%s','%s') " % (q[0], q[1], q[2], q[3], q[4], q[5], q[6]))
                del_id.append("'" + q[0] + "'")

            sql_insert = sql + ','.join(insert_data)
            delete_sql = del_sql % ','.join(del_id)
            session.execute(delete_sql)
            session.execute(sql_insert)
            session.commit()



if __name__ == '__main__':
    print '_____start_____'
    start = time.time()
    HotWarning().word_warning()
    HotWarning().target_warning()

    session.close()
    end = time.time()
    print '%.4f' % (end - start)