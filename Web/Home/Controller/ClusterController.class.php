<?php
namespace Home\Controller;
use Think\Controller;

class ClusterController extends Controller {
    
    //--  聚类分析
    public function api_cluster_analysis(){
        $model = M("text_cluster");
        $sql_1  = " SELECT size, quantity, add_datetime, keywords, value_list ";
        $sql_1 .= " FROM text_cluster ";
        $sql_1 .= " WHERE add_datetime = (SELECT MAX(add_datetime) FROM text_cluster) ";
        $sql_1 .= " ORDER BY quantity DESC ";
        $result_1 = $model->query($sql_1);
        $result = array();
        $result_all = array();
        foreach($result_1 as $i){
            $result['size'] = $i['size'];
            $result['quantity'] = $i['quantity'];
            $result['add_datetime'] = $i['add_datetime'];
            $result['keywords'] = $i['keywords'];
            $valueList = json_decode($i['value_list'],true);
            // var_dump($valueList);
            $dataList = array();
            foreach($valueList as $j){
                $Tid = $j['Tid'];
                $channeltype = $j['channeltype'];
                if($channeltype == 'news'){
                    $sql_query  = " SELECT Ttitle, Tpublish_datetime AS publish_datetime FROM news_text ";
                    $sql_query .= " WHERE id = '" .$Tid ."' ";
                    $query = $model->query($sql_query);
                    if (!empty($query[0])){
                        array_push($dataList, $query[0]);
                    }
                }
                if($channeltype == 'luntan'){
                    $sql_query  = " SELECT Ttitle, Tpublish_datetime AS publish_datetime FROM luntan_text ";
                    $sql_query .= " WHERE id = '" .$Tid ."' ";
                    $query = $model->query($sql_query);
                    if (!empty($query[0])){
                        array_push($dataList, $query[0]);
                    }
                }
                if($channeltype == 'tieba'){
                    $sql_query  = " SELECT Ttitle, Tpublish_datetime AS publish_datetime FROM tieba_text ";
                    $sql_query .= " WHERE id = '" .$Tid ."' ";
                    $query = $model->query($sql_query);
                    if (!empty($query[0])){
                        array_push($dataList, $query[0]);
                    }
                }
                if($channeltype == 'weibo'){
                    $sql_query  = " SELECT LEFT(content, 30) AS Ttitle, publish_datetime FROM t_sinablog ";
                    $sql_query .= " WHERE mid = '" .$Tid ."' ";
                    $query = $model->query($sql_query);
                    if (!empty($query[0])){
                        array_push($dataList, $query[0]);
                    }
                }
                if($channeltype == 'weixin'){
                    $sql_query  = " SELECT title AS Ttitle, publish_datetime FROM t_weixin ";
                    $sql_query .= " WHERE pid + ';' + wid = '" .$Tid ."' ";
                    $query = $model->query($sql_query);
                    if (!empty($query[0])){
                        array_push($dataList, $query[0]);
                    }
                }
            }
            $result['value_list'] = $dataList;
            array_push($result_all, $result);
            
            // break;
            
        }
        print json_encode($result_all);
    }
    
}
?>