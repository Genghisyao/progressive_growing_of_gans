<?php
namespace Home\Controller;
use Think\Controller;

class SearchController extends Controller {
    
    // 聚类关键词查询
    public function api_search_arcticle(){
        $word = $_POST['word'];
        // $word = '医院';
        $model = M("news_text");
        if(!empty($word)){
            $sql1  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql1 .= " FROM news_text ";
            $sql1 .= " JOIN translation ON site = eng ";
            $sql1 .= " WHERE Ttitle LIKE '%".$word."%' ";
            $sql1 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query1 = $model->query($sql1);
            
            $sql2  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql2 .= " FROM luntan_text ";
            $sql2 .= " JOIN translation ON 'bbs.tianya.cn' = eng ";
            $sql2 .= " WHERE Ttitle LIKE '%".$word."%' ";
            $sql2 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query2 = $model->query($sql2);
            
            $sql3  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql3 .= " FROM tieba_text ";
            $sql3 .= " JOIN translation ON 'tieba.baidu.com' = eng ";
            $sql3 .= " WHERE Ttitle LIKE '%".$word."%' ";
            $sql3 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query3 = $model->query($sql3);
            
            $sql4  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql4 .= " FROM zhihu_text ";
            $sql4 .= " JOIN translation ON 'zhihu.com' = eng ";
            $sql4 .= " WHERE Ttitle LIKE '%".$word."%' ";
            $sql4 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query4 = $model->query($sql4);
            
            $sql5  = " SELECT publish_datetime, LEFT(content, 30) AS title, chi AS media, content ";
            $sql5 .= " FROM t_sinablog ";
            $sql5 .= " JOIN translation ON 'weibo.com' = eng ";
            $sql5 .= " WHERE LEFT(content, 30) LIKE '%".$word."%' ";
            $sql5 .= " AND TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= 3 ";
            $query5 = $model->query($sql5);
            
            $sql6  = " SELECT publish_datetime, title, chi AS media, content  ";
            $sql6 .= " FROM t_weixin ";
            $sql6 .= " JOIN translation ON 'wx.qq.com' = eng ";
            $sql6 .= " WHERE title LIKE '%".$word."%' ";
            $sql6 .= " AND TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= 3 ";
            $query6 = $model->query($sql6);
            
            $result = array_merge($query1, $query2, $query3, $query4, $query5, $query6);
            print json_encode($result);
            
            
        }
    }
    
    // 云图关键词查询
    public function api_search_cloud(){
        $word = $_POST['word'];
        // $word = '医院';
        $model = M("news_text");
        if(!empty($word)){
            $sql1  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql1 .= " FROM news_text ";
            $sql1 .= " JOIN translation ON site = eng ";
            $sql1 .= " WHERE Ttitle LIKE '%".$word."%' ";
            // $sql1 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query1 = $model->query($sql1);
            
            $sql2  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql2 .= " FROM luntan_text ";
            $sql2 .= " JOIN translation ON 'bbs.tianya.cn' = eng ";
            $sql2 .= " WHERE Ttitle LIKE '%".$word."%' ";
            // $sql2 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query2 = $model->query($sql2);
            
            $sql3  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql3 .= " FROM tieba_text ";
            $sql3 .= " JOIN translation ON 'tieba.baidu.com' = eng ";
            $sql3 .= " WHERE Ttitle LIKE '%".$word."%' ";
            // $sql3 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query3 = $model->query($sql3);
            
            $sql4  = " SELECT Tpublish_datetime AS publish_datetime, Ttitle AS title, chi AS media, Tcontent AS content ";
            $sql4 .= " FROM zhihu_text ";
            $sql4 .= " JOIN translation ON 'zhihu.com' = eng ";
            $sql4 .= " WHERE Ttitle LIKE '%".$word."%' ";
            // $sql4 .= " AND TO_DAYS(NOW()) - TO_DAYS(Tpublish_datetime) <= 3 ";
            $query4 = $model->query($sql4);
            
            $sql5  = " SELECT publish_datetime, LEFT(content, 30) AS title, chi AS media, content ";
            $sql5 .= " FROM t_sinablog ";
            $sql5 .= " JOIN translation ON 'weibo.com' = eng ";
            $sql5 .= " WHERE LEFT(content, 30) LIKE '%".$word."%' ";
            // $sql5 .= " AND TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= 3 ";
            $query5 = $model->query($sql5);
            
            $sql6  = " SELECT publish_datetime, title, chi AS media, content  ";
            $sql6 .= " FROM t_weixin ";
            $sql6 .= " JOIN translation ON 'wx.qq.com' = eng ";
            $sql6 .= " WHERE title LIKE '%".$word."%' ";
            // $sql6 .= " AND TO_DAYS(NOW()) - TO_DAYS(publish_datetime) <= 3 ";
            $query6 = $model->query($sql6);
            
            $result = array_merge($query1, $query2, $query3, $query4, $query5, $query6);
            print json_encode($result);
            
            
        }
    }
}
?>