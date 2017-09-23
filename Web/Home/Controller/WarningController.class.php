<?php
namespace Home\Controller;
use Think\Controller;
use Think\Model;

class WarningController extends Controller {
    
    //--  预警显示
    public function api_get_warning(){
        $warning_list = M("warning_list");
        $result = array();
        // 热度预警
        $sql_1  = " SELECT a.*, b.event_name, c.chi ";
        $sql_1 .= " FROM warning_list a ";
        $sql_1 .= " INNER JOIN event_list b ";
        $sql_1 .= " ON a.event_id = b.event_id ";
        $sql_1 .= " INNER JOIN translation c ";
        $sql_1 .= " ON a.type = c.eng ";
        $sql_1 .= " WHERE type = 'heat' ";
        $sql_1 .= " GROUP BY a.event_id, type ";
        $sql_1 .= " ORDER BY `level`, FLOOR(data_value) DESC ";
        $result_1 = $warning_list->query($sql_1);
        
        // 媒体预警
        $sql_2  = " SELECT a.*, b.event_name, c.chi ";
        $sql_2 .= " FROM warning_list a ";
        $sql_2 .= " INNER JOIN event_list b ";
        $sql_2 .= " ON a.event_id = b.event_id ";
        $sql_2 .= " INNER JOIN translation c ";
        $sql_2 .= " ON a.type = c.eng ";
        $sql_2 .= " WHERE type = 'media' OR type = 'original' ";
        $sql_2 .= " GROUP BY a.event_id, type ";
        $sql_2 .= " ORDER BY `level` ";
        $result_2 = $warning_list->query($sql_2);
        
        // 地域预警
        $sql_3  = " SELECT a.*, b.event_name, c.chi ";
        $sql_3 .= " FROM warning_list a ";
        $sql_3 .= " INNER JOIN event_list b ";
        $sql_3 .= " ON a.event_id = b.event_id ";
        $sql_3 .= " INNER JOIN translation c ";
        $sql_3 .= " ON a.type = c.eng ";
        $sql_3 .= " WHERE type = 'province' OR type = 'netizen_number' ";
        $sql_3 .= " GROUP BY a.event_id, type ";
        $sql_3 .= " ORDER BY `level`, FLOOR(data_value) DESC ";
        $result_3 = $warning_list->query($sql_3);
        
        $result['heat_warning'] = $result_1;
        $result['media_warning'] = $result_2;
        $result['area_warning'] = $result_3;
        
        print json_encode($result);
    }
    
    //--  警戒线预警推送
    public function line_warning_push(){
        $data['add_datetime'] = $_POST['add_datetime'];
        $data['warning_type'] = $_POST['warning_type'];
        $data['condition'] = json_encode($_POST['condition']);
        $data['method'] = json_encode($_POST['method']);
        $warning_send = M("warning_send");
        $warning_send->add($data);
        print json_encode($data);
        
    }
    
    //--  指标阈值设置
    public function api_set_threshold(){
        $data_list = $_POST['data'];
        foreach($data_list as $k=>$v){
            $data['event_id'] = 1;
            $data['level'] = $v['level'];
            $data['threshold_reply'] = $v['threshold_reply'];
            $data['threshold_read'] = $v['threshold_read'];
            $data['threshold_forward'] = $v['threshold_forward'];
            $data['threshold_heat'] = $v['threshold_heat'];
            $data['threshold_channel'] = implode(',', $v['threshold_channel']);
            $data['threshold_original'] = $v['threshold_original'];
            $data['threshold_foreign'] = $v['threshold_foreign'];
            $data['threshold_province'] = $v['threshold_province'];
            $data['threshold_netizen'] = $v['threshold_netizen'];
            $data['event_nature'] = $v['event_nature'];
            $data['event_nature_word'] = $v['event_nature_word'];
            $data['netizen_emotion'] = $v['netizen_emotion'];
            $data['netizen_emotion_word'] = $v['netizen_emotion_word'];
            $warning_value = M("warning_value");
            // $sql = "select * from warning_value where `level`=".$data['level']." and event_id=".$data['event_id'];
            // $query = $warning_value->query($sql);
            $query = $warning_value->where("`level`='%s' and event_id='%s'", $data['level'], $data['event_id'])->find();
            if($query){
                $warning_value->save($data);
            }else{
                $warning_value->add($data);
            }
            
        }
        
        
    }
    
    //--  指标阈值展示
    public function api_get_threshold(){
        $warning_value = M("warning_value");
        $result_1 = $warning_value->where('event_id = 1')->select();
        print json_encode($result_1);
        
    }
    

}
