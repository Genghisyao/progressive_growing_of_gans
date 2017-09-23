<?php
namespace Home\Controller;
use Think\Controller;

class EventController extends Controller {
    
    //--  事件列表显示
    public function api_get_eventlist(){
        $event_list = M("event_list");
        $sql_1  = " SELECT a.*, b.crawl_datetime, b.reply_total, b.read_total, b.like_total, b.collect_total, b.original_total, b.forward_total, b.event_heat ";
        $sql_1 .= " FROM event_list a ";
        $sql_1 .= " LEFT JOIN (SELECT * FROM event_statistics_copy ORDER BY crawl_datetime DESC) b ";
        $sql_1 .= " ON a.event_id = b.event_id ";
        $sql_1 .= " GROUP BY a.event_id ";
        $sql_1 .= " ORDER BY add_datetime DESC ";
        $result_1 = $event_list->query($sql_1);
        print json_encode($result_1);
    }
    
    //--  事件修改
    public function api_update_eventlist(){
        $event_list = M("event_list");
        // $_POST['event_id'];
        $result = $event_list->where('event_id = %d', $_POST['event_id'])->select();
        print json_encode($result);
    }
    
    //--  事件添加
    public function api_set_eventlist(){
        $event_list = M("event_list");
        $data['event_name'] = $_POST['event_name'];
        $data['start_datetime'] = $_POST['start_datetime'];
        $data['keywords'] = $_POST['keywords'];
        $data['non_keywords'] = $_POST['non_keywords'];
        if($_POST['event_id'] == -1){
            $data['add_datetime'] = $_POST['add_datetime'];
            $event_list->add($data);
        }
        else{
            $data['event_id'] = $_POST['event_id'];
            $event_list->save($data);
        }
        $result = $event_list->select();
        print json_encode($result);
    }
    
    //--  事件删除
    public function api_delete_eventlist(){
        $event_list = M("event_list");
        $event_list->where("event_id='%s'", $_POST['event_id'])->delete();
        // $sql_drop  = "ALTER TABLE event_list DROP event_id;";
        // $sql_drop .= "ALTER TABLE event_list ADD event_id int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT FIRST;";
        // $event_list->execute($sql_drop);
    }
}
?>