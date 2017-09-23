<?php
namespace Home\Controller;
use Think\Controller;

// 热帖分析
class HotArticleController extends Controller {
    
    // 热帖列表
    public function api_get_hot_article_list(){
        $before_date = date('Y-m-d', strtotime('-7 days'));
        $sql = sprintf("
            SELECT Tid,title,publish_datetime,author_id,author_name,content,reply_count,read_count,
            like_count,collect_count,forward_count,chi AS channel,heat
            FROM hot_article 
            JOIN translation ON channel = eng
            WHERE publish_datetime > '%s'
        ", $before_date);
        $model = M("hot_article");
        $result = $model->query($sql);
        print json_encode($result);
    }
    
    // 7天最热文章
    public function api_get_hotest_article(){
        $before_date = date('Y-m-d', strtotime('-7 days'));
        $sql = sprintf("
            SELECT Tid,title,publish_datetime,author_id,author_name,content,reply_count,read_count,
            like_count,collect_count,forward_count,chi,heat
            FROM hot_article 
            JOIN translation ON channel = eng
            WHERE publish_datetime > '%s'
            ORDER BY heat DESC
            LIMIT 1
        ", $before_date);
        $model = M("hot_article");
        $result = $model->query($sql);
        print json_encode($result);
    }
    
    // 7天文章预警
    public function api_warning_hot_article(){
        $before_date = date('Y-m-d', strtotime('-7 days'));
        $sql = sprintf("
            SELECT haw.Tid, haw.`level`, haw.warning_datetime, t1.chi AS type, haw.threshold_value, haw.reason, haw.data_value,
            ha.title, ha.publish_datetime, ha.author_id, ha.author_name, ha.content, t2.chi AS channel
            FROM hot_article_warning haw
            LEFT JOIN hot_article ha
            ON haw.Tid = ha.Tid
            LEFT JOIN translation t1
            ON haw.type = t1.eng
            LEFT JOIN translation t2
            ON ha.channel = t2.eng
            WHERE ha.publish_datetime > '%s'
            ORDER BY haw.`level` , haw.warning_datetime DESC
        ", $before_date);
        $model = M("hot_article");
        $result = $model->query($sql);
        print json_encode($result);
    }
    
    
}
?>