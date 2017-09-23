<?php
namespace Home\Controller;
use Think\Controller;

class HomeController extends Controller {
    
    //--  热点视图
    public function api_get_topview(){
        $model2 = M("text_select_copy");
        $result = array();
        $before_date = date('Y-m-d', strtotime('-7 days'));
        
        // 7天内最新文章
        $sql_2 = sprintf("
            SELECT a.title, a.add_datetime, a.publish_datetime, a.content, a.author_id, a.author_name, c.chi, b.heat
            FROM (SELECT * FROM text_select_copy WHERE add_datetime > '%s' ORDER BY add_datetime DESC LIMIT 1) a
            LEFT JOIN text_analysis b
            ON a.Tid = b.Tid
            LEFT JOIN translation c
            ON a.channel = c.eng
            ORDER BY crawl_datetime DESC LIMIT 1
        ", $before_date);
        $result_2 = $model2->query($sql_2);
        
        // 7天内最热文章
        $sql_3 = sprintf("
            SELECT Tid,title,publish_datetime,author_id,author_name,content,reply_count,read_count,
            like_count,collect_count,forward_count,chi,heat
            FROM hot_article 
            JOIN translation ON channel = eng
            WHERE publish_datetime > '%s'
            ORDER BY heat DESC
            LIMIT 1
        ", $before_date);
        $result_3 = $model2->query($sql_3);
        
        // 最热媒体
        // $sql_4  = " SELECT b.chi, a.media_heat ";
        // $sql_4 .= " FROM media_statistics a ";
        // $sql_4 .= " INNER JOIN translation b ";
        // $sql_4 .= " ON a.channel = b.eng ";
        // $sql_4 .= " WHERE event_id = 0 ";
        // $sql_4 .= " ORDER BY crawl_datetime DESC, media_heat DESC LIMIT 1 ";
        // $result_4 = $model2->query($sql_4);
        
        $result['top_new'] = $result_2;
        $result['top_heat'] = $result_3;
        // $result['top_media'] = $result_4;
        print json_encode($result);
    }
    
    //--  事件总览
    public function api_get_overview(){
        $startDate = date("Y-m-d", strtotime("-60 days")); 
        // endDate = date("Y-m-d");
        $event_list = M("event_list");
        $event_stat = M("event_statistics_copy");
        $result_all = array();
        
        // 总量
        // $sql_1  = " SELECT crawl_datetime, SUM(original_total) AS original_total FROM ";
        // $sql_1 .= " (SELECT event_id, DATE_FORMAT(crawl_datetime,'%Y-%m-%d') AS crawl_datetime, MAX(original_total) AS original_total ";
        // $sql_1 .= " FROM event_statistics_copy ";
        // $sql_1 .= " WHERE event_id > 0 ";
        // $sql_1 .= " AND TO_DAYS(crawl_datetime) > TO_DAYS('2017-07-18') ";
        // $sql_1 .= " GROUP BY event_id, TO_DAYS(crawl_datetime)) a ";
        // $sql_1 .= " GROUP BY crawl_datetime ";
        // $result_1 = $event_stat->query($sql_1);
        
        $sql_event = sprintf("
            SELECT *
            FROM event_list
            WHERE add_datetime > '%s'
            ORDER BY add_datetime DESC
            limit 6
        ", $startDate);
        $result_list = $event_list->query($sql_event);
        $item = array();
        $result = array();
        $result_w = array();
        foreach($result_list as $i){
            // 热度变化曲线
            $event_id = $i['event_id'];
            $event_name = $i['event_name'];
            $sql_2  = " SELECT b.event_id, b.crawl_datetime, IFNULL(b.event_heat-c.event_heat, 0) AS event_heat ";
            $sql_2 .= " FROM ";
            $sql_2 .= " (SELECT event_id, DATE_FORMAT(crawl_datetime,'%Y-%m-%d') AS crawl_datetime, MAX(event_heat) AS event_heat ";
            $sql_2 .= " FROM event_statistics_copy ";
            $sql_2 .= " GROUP BY event_id, TO_DAYS(crawl_datetime)) b ";
            $sql_2 .= " LEFT JOIN ";
            $sql_2 .= " (SELECT event_id, DATE_FORMAT(crawl_datetime,'%Y-%m-%d') AS crawl_datetime, MAX(event_heat) AS event_heat ";
            $sql_2 .= " FROM event_statistics_copy ";
            $sql_2 .= " GROUP BY event_id, TO_DAYS(crawl_datetime)) c ";
            $sql_2 .= " ON b.event_id = c.event_id AND TO_DAYS(b.crawl_datetime) = TO_DAYS(c.crawl_datetime) + 2 ";
            $sql_2 .= " WHERE b.event_id = " . $event_id;
            // $sql_2 .= " AND TO_DAYS(b.crawl_datetime) > TO_DAYS('2017-07-18') ";
            $result_2 = $event_stat->query($sql_2);
            
            // 预警点获取
            $sql_4 = sprintf("
                SELECT DATE_FORMAT(warning_datetime,'%%Y-%%m-%%d') AS warning_datetime, event_id, `level`, reason, chi 
                FROM warning_list 
                LEFT JOIN translation
                ON eng = type
                WHERE event_id = %d GROUP BY type
            ", $event_id);
            $result_4 = $event_stat->query($sql_4);
            
            $result_2_1 = array();
            foreach($result_2 as $i){
                // 热度变换转为对数
                if($i['event_heat'] < M_E){
                    $e = $i['event_heat'];
                }
                else{
                    $e = round(log($i['event_heat']),2);
                }
                array_push($result_2_1, array('event_id'=>$i['event_id'], 'crawl_datetime'=>$i['crawl_datetime'], 'event_heat'=>$e));
                
                // 预警打点对应热度曲线
                foreach($result_4 as $j){
                    if($j['warning_datetime']==$i['crawl_datetime']){
                        $data = array();
                        $data['warning_datetime'] = $j['warning_datetime'];
                        $data['deta_heat'] =  $e;
                        $data['chi'] = $j['chi'] ;
                        $data['event_name'] = $event_name ;
                        $data['level'] = $j['level'] ;
                        $data['reason'] = $j['reason'] ;
                        array_push($result_w, $data);
                    }
                }
            }
            $item['event_name'] = $event_name;
            $item['info'] = $result_2_1;
            array_push($result, $item);
        
        }
        // 按热度排序
        foreach ($result as $key => $row){
            $event_heat[$key]  = $row['event_heat'];
        }
        array_multisort($event_heat, SORT_ASC, $result);
        

        // $result_all['total_amount'] = $result_1;
        $result_all['event'] = $result;
        $result_all['warning_info'] = $result_w;
        print json_encode($result_all);
    }
    
    //--  各事件关键词云图
    public function api_get_heatwords(){
        $event_stat = M("event_heatwords");
        $sql_1  = " SELECT words_name, words_weight ";
        $sql_1 .= " FROM event_heatwords ";
        $sql_1 .= " WHERE event_id = 0 AND crawl_datetime = (SELECT MAX(crawl_datetime) FROM event_heatwords) ";
        $sql_1 .= " ORDER BY words_weight DESC ";
        $result_1 = $event_stat->query($sql_1);
        // $result_1 = array();
        // $a1 = array('words_name'=>iconv('gb2312','utf-8','限外'), 'words_weight'=>0.053159);
        // $a2 = array('words_name'=>iconv('gb2312','utf-8','双鸭山'), 'words_weight'=>0.040463);
        // $a3 = array('words_name'=>iconv('gb2312','utf-8','校友'), 'words_weight'=>0.026741);
        // $a4 = array('words_name'=>iconv('gb2312','utf-8','开放'), 'words_weight'=>0.022478);
        // $a5 = array('words_name'=>iconv('gb2312','utf-8','巡视组'), 'words_weight'=>0.022381);
        // $a6 = array('words_name'=>iconv('gb2312','utf-8','校徽'), 'words_weight'=>0.021325);
        // $a7 = array('words_name'=>iconv('gb2312','utf-8','时代地产'), 'words_weight'=>0.016463);
        // $a8 = array('words_name'=>iconv('gb2312','utf-8','管理'), 'words_weight'=>0.015207);
        // $a9 = array('words_name'=>iconv('gb2312','utf-8','进入'), 'words_weight'=>0.015195);
        // $a10 = array('words_name'=>iconv('gb2312','utf-8','社会人员'), 'words_weight'=>0.014536);
        // $a11 = array('words_name'=>iconv('gb2312','utf-8','安全'), 'words_weight'=>0.013487);
        // $a12 = array('words_name'=>iconv('gb2312','utf-8','教学楼'), 'words_weight'=>0.013194);
        // $a13 = array('words_name'=>iconv('gb2312','utf-8','参观'), 'words_weight'=>0.012837);
        // $a14 = array('words_name'=>iconv('gb2312','utf-8','教学秩序'), 'words_weight'=>0.012795);
        // $a15 = array('words_name'=>iconv('gb2312','utf-8','党委'), 'words_weight'=>0.011654);
        // $a16 = array('words_name'=>iconv('gb2312','utf-8','发展'), 'words_weight'=>0.011520);
        // $a17 = array('words_name'=>iconv('gb2312','utf-8','限制'), 'words_weight'=>0.011484);
        // $a18 = array('words_name'=>iconv('gb2312','utf-8','身份证'), 'words_weight'=>0.011418);
        // $a19 = array('words_name'=>iconv('gb2312','utf-8','规定'), 'words_weight'=>0.011361);
        // $a20 = array('words_name'=>iconv('gb2312','utf-8','整改'), 'words_weight'=>0.011262);
        // $a21 = array('words_name'=>iconv('gb2312','utf-8','校长'), 'words_weight'=>0.010842);
        // $a22 = array('words_name'=>iconv('gb2312','utf-8','捐赠'), 'words_weight'=>0.010661);
        // $a23 = array('words_name'=>iconv('gb2312','utf-8','出示'), 'words_weight'=>0.010619);
        // $a24 = array('words_name'=>iconv('gb2312','utf-8','保安'), 'words_weight'=>0.010508);
        // array_push($result_1, $a1,$a2,$a3,$a4,$a5,$a6,$a7,$a8,$a9,$a10,$a11,$a12,$a13,$a14,$a15,$a16,$a17,$a18,$a19,$a20,$a21,$a22,$a23,$a24);
        print json_encode($result_1);
    }
    
    //--  各事件历史最高热度排行榜
    public function api_get_highest(){
        $event_stat = M("event_statistics");
        $sql_1  = " SELECT a.event_id, a.event_name, MAX(b.event_heat) as highest_heat ";
        $sql_1 .= " FROM event_list a LEFT JOIN event_statistics_copy b ";
        $sql_1 .= " ON a.event_id = b.event_id ";
        $sql_1 .= " GROUP BY a.event_id ";
        $sql_1 .= " ORDER BY highest_heat DESC ";
        $result_1 = $event_stat->query($sql_1);
        print json_encode($result_1);
    }
    
    //--  各事件热度变化排行榜
    public function api_get_change(){
        $event_stat = M("event_statistics");
        $sql_1  = " SELECT a.event_id, a.event_name, (b.event_heat-c.event_heat)-(c.event_heat-d.event_heat) AS deta_week_heat ";
        $sql_1 .= " FROM event_list a ";
        $sql_1 .= " LEFT JOIN (SELECT event_id, MAX(event_heat) as event_heat FROM event_statistics_copy WHERE TO_DAYS(crawl_datetime) = TO_DAYS(NOW()) GROUP BY event_id) b ";
        $sql_1 .= " ON a.event_id = b.event_id ";
        $sql_1 .= " LEFT JOIN (SELECT event_id, MAX(event_heat) as event_heat FROM event_statistics_copy WHERE TO_DAYS(crawl_datetime) = TO_DAYS(NOW())-3 GROUP BY event_id) c ";
        $sql_1 .= " ON a.event_id = c.event_id ";
        $sql_1 .= " LEFT JOIN (SELECT event_id, MAX(event_heat) as event_heat FROM event_statistics_copy WHERE TO_DAYS(crawl_datetime) = TO_DAYS(NOW())-6 GROUP BY event_id) d ";
        $sql_1 .= " ON a.event_id = d.event_id ";
        $sql_1 .= " ORDER BY deta_week_heat DESC ";
        $result_1 = $event_stat->query($sql_1);
        // print_r($result_1);
        print json_encode($result_1);
        
        // $result = array();
        // foreach($result_1 as $i){
            // if($i['event_heat']==''){
                // $trend = '暂无';
            // }
            // if($i['deta_week_heat']==0){
                // if($i['event_heat']==$i['event_heat1']){
                // $trend = '消退';
            // }
                // $trend = '上升';
            // }
            // if($i['deta_week_heat']>0){
                // $trend = '上升';
            // }
            // if($i['deta_week_heat']<0){
                // $trend = '下降';
            // }
            
        // }
        // print json_encode($result);
    }
}
?>