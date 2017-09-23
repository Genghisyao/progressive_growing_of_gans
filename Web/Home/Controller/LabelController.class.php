<?php
namespace Home\Controller;
use Think\Controller;

class LabelController extends Controller {
    
    //-- 获取文章性质标注
    public function api_get_article_nature(){
        $model = M("text_select_copy");
        $sql_1 = " 
        SELECT count(*) AS total_count
        FROM text_select_copy
        WHERE article_nature IS NULL
        OR article_nature = ''
        ";
        $result_1 = $model->query($sql_1);
        $sql_2 = " 
        SELECT title, content, Tid, event_id, channel
        FROM text_select_copy
        WHERE article_nature IS NULL
        OR article_nature = ''
        ORDER BY add_datetime
        LIMIT 100
        ";
        $result_2 = $model->query($sql_2);
        $result['total_count'] = $result_1[0]['total_count'];
        $result['result'] = $result_2;
        print json_encode($result);
    }
    
    //-- 更新文章性质标注
    public function api_set_article_nature(){
        $model = M("text_select_copy");
        if(IS_POST){
            $data_list = $_POST['data'];
            print $data_list;
            print json_encode($data_list);
            foreach($data_list as $k=>$v){
                $data['Tid'] = $v['tid'];
                $data['event_id'] = $v['event_id'];
                $data['channel'] = $v['channel'];
                $data['article_nature'] = $v['article_nature'];
                $model->save($data);
                
            }
        }
        
        
    }
    
}

?>