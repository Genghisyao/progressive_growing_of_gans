<?php
namespace Home\Controller;
use Think\Controller;

// 关注人群
class AttentionController extends Controller {
    
    //--  地理位置
    public function api_get_location(){
        $event_id = $_POST['event_id'];
        // $event_id = 1;
        $model = M("text_select_comment");
        $result_all = array();
        
        // 全国
        $sql_1  = " SELECT region, count(*) AS number ";
        $sql_1 .= " FROM ( ";
        $sql_1 .= " SELECT substring_index(substring_index(ip_address,';',2),';',-1) AS region ";
        $sql_1 .= " FROM text_select_comment ";
        $sql_1 .= " WHERE ip_address LIKE '中国%' AND event_id = " .$event_id;
        $sql_1 .= " ) AS a ";
        $sql_1 .= " GROUP BY region ";
        $sql_1 .= " ORDER BY number DESC ";
        $query_1 = $model->query($sql_1);
        $result_1 = $query_1;
        // print json_encode($result_1);
        
        // 省内
        $sql_2  = " SELECT city, count(*) AS number ";
        $sql_2 .= " FROM ( ";
        $sql_2 .= " SELECT substring_index(ip_address,';',-1) AS city ";
        $sql_2 .= " FROM text_select_comment ";
        $sql_2 .= " WHERE ip_address LIKE '中国;广东;%' AND event_id = " .$event_id;
        $sql_2 .= " ) AS a ";
        $sql_2 .= " WHERE city <> '' ";
        $sql_2 .= " GROUP BY city ";
        $sql_2 .= " ORDER BY number DESC ";
        $query_2 = $model->query($sql_2);
        $result_2 = $query_2;
        // print json_encode($result_2);
        
        $result_all['China'] = $result_1;
        $result_all['Guangdong'] = $result_2;
        print json_encode($result_all);
        
    }

}
?>