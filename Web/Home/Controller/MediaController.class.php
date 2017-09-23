<?php
namespace Home\Controller;
use Think\Controller;

// 媒体分析
class MediaController extends Controller {
    
    // 所有媒体统计表
    public function api_all_media_statistics(){
        $model = M("media_statistics");
        $sql_1  = " SELECT reply_total, read_total, like_total, collect_total, original_total, forward_total, chi AS channel, media_heat ";
        $sql_1 .= " FROM media_statistics ";
        $sql_1 .= " LEFT JOIN translation ";
        $sql_1 .= " ON channel = eng ";
        $sql_1 .= " WHERE event_id = 0 AND crawl_datetime = (SELECT MAX(crawl_datetime) FROM media_statistics) ";
        $sql_1 .= " ORDER BY media_heat DESC ";
        $result_1 = $model->query($sql_1);
        print json_encode($result_1);
    }
        
    //--  传播链分析
    public function api_get_transmission(){
        $event_id = $_POST['event_id'];
        $model = M("text_select_copy");
        // $sql_1  = " SELECT publish_datetime, title, content, channel, chi, author_name, heat FROM ";
        // $sql_1 .= " (SELECT publish_datetime, title, content, a.channel, chi, author_name, heat ";
        // $sql_1 .= " FROM text_select_copy a ";
        // $sql_1 .= " LEFT JOIN (SELECT * FROM text_analysis WHERE crawl_datetime = (SELECT MAX(crawl_datetime) FROM text_analysis)) b ";
        // $sql_1 .= " ON a.Tid = b.Tid AND a.event_id = b.event_id AND a.channel = b.channel ";
        // $sql_1 .= " LEFT JOIN translation ";
        // $sql_1 .= " ON a.channel = eng ";
        // $sql_1 .= " WHERE a.event_id = " .$event_id;
        // $sql_1 .= " ORDER BY publish_datetime) c ";
        // $sql_1 .= " GROUP BY channel ";
        // $sql_1 .= " ORDER BY heat DESC ";
        
        $sql_1 = sprintf("
            SELECT t1.publish_datetime, t1.title, t1.content, t1.author_id, t1.author_name, t1.channel, t3.chi, MAX(t2.heat) AS heat
            FROM (
            SELECT Tid, event_id, channel, min(publish_datetime) AS publish_datetime, title, content, author_id, author_name
            FROM text_select_copy
            WHERE event_id = %d
            GROUP BY channel
            ) t1
            LEFT JOIN text_analysis t2
            ON t1.Tid = t2.Tid AND t1.event_id = t2.event_id AND t1.channel = t2.channel
            LEFT JOIN translation t3
            ON t1.channel = t3.eng
            GROUP BY t1.channel
            ORDER BY publish_datetime
        ", $event_id);
        
        $result_1 = $model->query($sql_1);
        print json_encode($result_1);
        
    }
    
    //--  追踪报道
    public function api_get_follow(){
        $event_id = $_POST['event_id'];        
        $model = M("media_statistics");
        // $sql_1  = " SELECT chi AS channel, original_total, reply_total, read_total, like_total, collect_total, forward_total ";
        // $sql_1 .= " FROM media_statistics ";
        // $sql_1 .= " LEFT JOIN translation ";
        // $sql_1 .= " ON channel = eng ";
        // $sql_1 .= " WHERE event_id = " .$event_id;
        // $sql_1 .= " AND crawl_datetime = (SELECT MAX(crawl_datetime) FROM media_statistics) ";
        // $sql_1 .= " GROUP BY channel ";
        // $sql_1 .= " ORDER BY original_total DESC ";
        $sql_1 = sprintf("
            SELECT MAX(crawl_datetime) AS crawl_datetime, chi AS channel, original_total, reply_total, read_total, like_total, collect_total, forward_total
            FROM media_statistics
            LEFT JOIN translation
            ON channel = eng
            WHERE event_id = %d
            GROUP BY channel
            ORDER BY original_total DESC
        ", $event_id);
        $result_1 = $model->query($sql_1);
        
        
        $sql_2  = " SELECT title, author_name, publish_datetime, chi AS channel, a.reply_count, a.read_count, a.like_count, a.collect_count, a.forward_count, b.heat, a.article_nature ";
        $sql_2 .= " FROM text_select_copy a ";
        $sql_2 .= " LEFT JOIN (SELECT event_id, Tid, channel, heat FROM text_analysis WHERE crawl_datetime = (SELECT MAX(crawl_datetime) FROM text_analysis)) b ";
        $sql_2 .= " ON a.event_id = b.event_id AND a.Tid = b.Tid AND a.channel = b.channel ";
        $sql_2 .= " LEFT JOIN translation ";
        $sql_2 .= " ON a.channel = eng ";
        $sql_2 .= " WHERE a.event_id = " .$event_id;
        $sql_2 .= " GROUP BY a.event_id, a.Tid, a.channel ";
        $sql_2 .= " ORDER BY a.publish_datetime DESC ";
        $sql_2 .= " LIMIT 200 ";
        $result_2 = $model->query($sql_2);
        
        $result = array('channelRank'=>$result_1, 'articleRank'=>$result_2);
        print json_encode($result);
    }
    
    //--  友好度分析
    public function api_get_friendly(){
        $event_id = $_POST['event_id'];
        $model = M("text_select_copy");
        $event_id = 1;
        $sql_1 = sprintf("
            SELECT chi AS channel, a.total, COALESCE(a.total - b.negative, a.total) AS positive, COALESCE(b.negative, 0) AS negative, IF(b.negative IS NULL, 1.0000, 1 - b.negative/a.total) AS friendly
            FROM (SELECT channel, COUNT(1) AS total
            FROM text_select_copy
            WHERE (article_nature IS NOT NULL OR auto_article_nature IS NOT NULL)
            AND event_id = %d
            GROUP BY channel) a
            LEFT JOIN
            (SELECT channel, COUNT(1) AS negative
            FROM text_select_copy
            WHERE (article_nature IS NOT NULL OR auto_article_nature IS NOT NULL)
            AND (article_nature = 'negative' OR auto_article_nature = 'negative')
            AND event_id = %d
            GROUP BY channel) b
            ON a.channel = b.channel
            LEFT JOIN
            translation
            ON a.channel = eng
        ", $event_id, $event_id);
        $result_1 = $model->query($sql_1);
        
        $sql_2 = sprintf("
            SELECT COUNT(1) AS total
            FROM text_select_copy
            WHERE (article_nature IS NOT NULL OR auto_article_nature IS NOT NULL)
            AND event_id = %d
        ", $event_id);
        $result_2 = $model->query($sql_2);
        
        $result = array();
        foreach($result_1 as $i){
            $data = array();
            $data['channel'] = $i['channel'];
            $data['friendly'] = round((($i['positive'] - $i['negative']) / $i['total'] * 100),2);
            $data['influnce'] = round(($i['total'] / $result_2[0]['total'] * 100),2);
            array_push($result, $data);
        }
        print json_encode($result);
    }
}
?>