<?php
namespace Home\Controller;
use Think\Controller;
class ReportController extends Controller {
    
    //--  事件传播波形图
    public function api_get_read(){
        $event_id = $_POST['event_id'];
        $model = M("event_statistics_copy");
        $sql_1  = " SELECT DATE_FORMAT(crawl_datetime,'%Y/%m/%d') AS crawl_datetime , read_total, event_heat ";
        $sql_1 .= " FROM (SELECT * FROM event_statistics_copy ORDER BY crawl_datetime) a ";
        $sql_1 .= " WHERE a.event_id = " .$event_id;
        $sql_1 .= " GROUP BY TO_DAYS(crawl_datetime) ";
        $result_1 = $model->query($sql_1);
        print json_encode($result_1);
    }
    
    //--  单事件报告下载
    public function api_download_eventreport(){
        $event_id = $_POST['event_id'];
        $event_id = intval($event_id, 10);
        // $event_id = 1;
        // $event_id = 7;
        require('xmlrpc.inc.php');
        $client = new \xmlrpc_client('/', 'localhost', '5060');
        $client->setDebug(0);
        $client->request_charset_encoding='utf-8';
        $client->debug=False;
        $result = array ("state"=>200,"title"=>"OK");
        try {
            $data = array(php_xmlrpc_encode($event_id));
            $param = new \xmlrpcmsg('downloadEventReport', $data);
            $ret = $client->send($param);
            
            if(!$ret->faultCode()) {
                $val = $ret->value();
                print_r(php_xmlrpc_decode($val));
                
                // foreach(php_xmlrpc_decode($val) as $key => $value){
                    // $status[$key] = $value;
                // }
                
            } else {
                $result["state"] = 114;
            }
        } catch (Exception $e) {
            $result["state"] = 104;
        }
        // 下载文件
        $model = M('event_list');
        $sql_1 = 'SELECT event_name FROM event_list WHERE event_id = '. $event_id;
        $result_1 = $model->query($sql_1);
        foreach($result_1 as $i){
            $event_name = $i['event_name'];
            break;
        }
        $fileName = '《' . $event_name. '》报告' . date("Ymd") . '.docx';
        $filePath = "python/reports/" . $fileName;
        if(file_exists($filePath)) {
            header('Location: '.C("WEB_ROOT").$filePath);
            // echo("<h2>下载完成</h2>");
        }else{
            echo("<h2>文件不存在</h2>");
        }
    }
    
    //--  所有事件报告下载
    public function api_download_viewreport(){
        require('xmlrpc.inc.php');
        $client = new \xmlrpc_client('/', 'localhost', '5060');
        $client->setDebug(0);
        $client->request_charset_encoding='utf-8';
        $client->debug=False;
        $result = array ("state"=>200,"title"=>"OK");
        try {
            $param = new \xmlrpcmsg('downloadViewReport');
            $ret = $client->send($param);
            
            if(!$ret->faultCode()) {
                $val = $ret->value();
                print_r(php_xmlrpc_decode($val));
                
                // foreach(php_xmlrpc_decode($val) as $key => $value){
                    // $status[$key] = $value;
                // }
                
            } else {
                $result["state"] = 114;
            }
        } catch (Exception $e) {
            $result["state"] = 104;
        }
        // 下载文件
        $fileName = '事件总览报告' . date("Ymd") . '.docx';
        $filePath = "python/reports/" . $fileName;
        if(file_exists($filePath)) {
            header('Location: '.C("WEB_ROOT").$filePath);
            // echo("<h2>下载完成</h2>");
        }else{
            echo("<h2>文件不存在</h2>");
        }
    }
    
}
?>