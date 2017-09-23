<?php
namespace Home\Controller;
use Think\Controller;

// 热度分析
class HeatController extends Controller {
        
    //--  热度走势分析
    public function api_get_trend(){
        $event_id = $_POST['event_id'];
        // $event_id = 1;
        // $model = M("event_statistics_copy");
        // $sql_1  = " SELECT a.event_id,event_name,crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total,event_heat ";
        // $sql_1 .= " FROM event_statistics_copy a ";
        // $sql_1 .= " LEFT JOIN event_list b ";
        // $sql_1 .= " ON a.event_id = b.event_id ";
        // $sql_1 .= " WHERE a.event_id = " .$event_id;
        // $sql_1 .= " GROUP BY a.crawl_datetime DESC ";
        // $result_1 = $model->query($sql_1);
        // print json_encode($result_1);
        
        $model = M("event_statistics_copy");
        $result = array();
        $sql_1  = " SELECT crawl_datetime,reply_total,read_total,like_total,collect_total,original_total,forward_total ";
        $sql_1 .= " FROM event_statistics_copy ";
        $sql_1 .= " WHERE event_id = " .$event_id;
        $sql_1 .= " AND crawl_datetime = (SELECT MAX(crawl_datetime) FROM event_statistics_copy) ";
        $result_1 = $model->query($sql_1);
        // print json_encode($result_1);
        
        $sql_2  = " SELECT b.crawl_datetime, IFNULL(b.event_heat-c.event_heat, 0) AS event_heat ";
        $sql_2 .= " FROM ";
        $sql_2 .= " (SELECT event_id, DATE_FORMAT(crawl_datetime,'%Y-%m-%d') AS crawl_datetime, MAX(event_heat) AS event_heat ";
        $sql_2 .= " FROM event_statistics_copy ";
        $sql_2 .= " GROUP BY event_id, TO_DAYS(crawl_datetime)) b ";
        $sql_2 .= " LEFT JOIN ";
        $sql_2 .= " (SELECT event_id, DATE_FORMAT(crawl_datetime,'%Y-%m-%d') AS crawl_datetime, MAX(event_heat) AS event_heat ";
        $sql_2 .= " FROM event_statistics_copy ";
        $sql_2 .= " GROUP BY event_id, TO_DAYS(crawl_datetime)) c ";
        $sql_2 .= " ON b.event_id = c.event_id AND TO_DAYS(b.crawl_datetime) = TO_DAYS(c.crawl_datetime)+2 ";
        $sql_2 .= " WHERE b.event_id = " . $event_id;
        $sql_2 .= " AND TO_DAYS(b.crawl_datetime) > TO_DAYS('2017-07-18') ";
        $result_2 = $model->query($sql_2);
        // print json_encode($result_2);
        
        $result['statistics'] = $result_1;
        $result['heat'] = $result_2;
        print json_encode($result);
        
    }
    
    //--  热门分析
    public function api_get_article(){
        $event_id = $_POST['event_id'];
        // $event_id = 1;
        // $model = M("text_select");
        // $sql_1  = " SELECT publish_datetime, title, heat, channel, chi, author_name ";
        // $sql_1 .= " FROM text_select ";
        // $sql_1 .= " LEFT JOIN translation ";
        // $sql_1 .= " ON channel = eng ";
        // $sql_1 .= " WHERE event_id = " .$event_id;
        // $sql_1 .= " ORDER BY heat DESC ";
        // $result_1 = $model->query($sql_1);
        // print json_encode($result_1);
        
        $model = M("text_select_copy");
        $sql_1  = " SELECT publish_datetime, title, author_name, a.channel, chi, heat ";
        $sql_1 .= " FROM text_select_copy a ";
        $sql_1 .= " LEFT JOIN (SELECT event_id, Tid, channel, heat FROM text_analysis WHERE crawl_datetime = (SELECT MAX(crawl_datetime) FROM text_analysis)) b ";
        $sql_1 .= " ON a.Tid = b.Tid AND a.event_id = b.event_id AND a.channel = b.channel ";
        $sql_1 .= " LEFT JOIN translation ";
        $sql_1 .= " ON a.channel = eng ";
        $sql_1 .= " WHERE a.event_id = " .$event_id;
        $sql_1 .= " GROUP BY a.Tid, a.event_id, a.channel ";
        $sql_1 .= " ORDER BY heat DESC ";
        $sql_1 .= " LIMIT 200 ";
        $result_1 = $model->query($sql_1);
        print json_encode($result_1);
    }
}
?>