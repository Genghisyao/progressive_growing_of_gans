<?php
namespace Home\Controller;
use Think\Controller;

class IndexController extends Controller {
    
    public function index(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('domain', C("SITE_DOMAIN_NAME"));
        $this->assign('showName', S($authKey.":showName"));
        $keyword = $_GET['keyword'];
        $channel = $_GET['channel'];
        $this->assign('keyword',$keyword);
        $this->assign('channel',$channel);
        $this->display();
    }
    
    public function mytheme(){
        $webRoot = C("WEB_ROOT");
        $chooseName=I("path.3");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('chooseName',$chooseName);
        $this->display();
    }
    
    public function mysourcedata(){
        /*$postData=$_POST;*/
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        /*$this->assign('postdata',json_encode($postData));*/
        $this->display();
    }
    
    public function mytable(){
        /*$postData = $_POST;*/
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
       
        $this->assign('webroot', C("WEB_ROOT"));
        /*$this->assign('postdata',json_encode($postData));*/
        $this->display();
        
    }
    
    public function sourcedata(){
        /*$bodyId = ' id="'.I("path.2").'" ';*/
        /*$eventName=I("path.2");*/
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        /*$this->assign('bodyid', $bodyId);*/
        /*$this->assign('eventname',$eventName);*/
        $this->display();
    }

    public function page2(){
        /*$bodyId = ' id="'.I("path.2").'" ';*/
        $keyName=I("path.2");
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('keyName', $keyName);
        /*$this->assign('eventname',$eventName);*/
        $this->display();
    }

    public function tablev1(){
        
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
    
    public function warning(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $id=I("path.2");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('id',$id);
        $this->display();
    }
    
    public function table(){
        /*$bodyId = ' id="'.I("path.2").'" ';*/
        $chooseName=I("path.3");
        $jsonText=I("param.jsontext");
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $id=I("path.2");
        $title=I("path.4");
        $this->assign('webroot', C("WEB_ROOT"));
        /*$this->assign('bodyid', $bodyId);*/
        $this->assign('choosename',$chooseName);
        $this->assign('jsontext',$jsonText);
        $this->assign('id',$id);
        $this->assign('title',$title);
        $this->display();
    }
    
    public function priviledge(){
        /*$bodyId = ' id="'.I("path.2").'" ';*/
        $chooseName=I("path.2");
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('chooseName', $chooseName);
        $this->display();
    }
    
    public function data_filtered(){
        /*$bodyId = ' id="'.I("path.2").'" ';*/
        $chooseName=I("param.name");
        $areaName=I("param.area");
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $id=I("path.2");
        $this->assign('webroot', C("WEB_ROOT"));
        /*$this->assign('bodyid', $bodyId);*/
        $this->assign('choosename',$chooseName);
        $this->assign('areaname',$areaName);
        $this->assign('id',$id);
        $this->display();
    }
    
    public function data_model(){
        $bodyId = ' id="'.I("path.2").'" ';
        $chooseName=I("path.3");
        /*$chooseName = I("param.cname");*/
        /*html_entity_decode($chooseName,ENT_QUOTES);*/

        /*$jsonTest=I("param.test");*/
        $id=I("path.4");
        $postData = $_POST;
        \Think\Log::record(json_encode($postData));
        
        \Think\Log::record($chooseName, 'WARN');
        \Think\Log::record(I("param.keywords"), 'WARN');

        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        htmlspecialchars_decode($chooseName,ENT_QUOTES);
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('bodyid', $bodyId);
        $this->assign('postdata',json_encode($postData));
        $this->assign('choosename',$chooseName);
        $this->assign('id',$id);
        /*$this->assign('jsontest',$jsonTest);*/
        $this->display();
    }
    
    public function menu_data(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
    
    public function menu_setting(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
    
    public function menu_export(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
    
    public function mark(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
        
    public function hotArticleList(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }

    public function menu_model(){
        $myId = $this->assignCommon();
        $webRoot = C("WEB_ROOT");
        $this->assign('webroot', C("WEB_ROOT"));
        $this->display();
    }
    //--  传播链分析
    public function api_get_transmission(){
        // $myId = $this->assignCommon();
        $keyword = $_POST['keyword'];
        $channel = $_POST['channel'];
        $Model = new \Think\Model();
        $sql_0 = "select publish_datetime, b.chi as media from text_select a left join translation b on a.channel = b.eng order by publish_datetime asc";
        $sql_1 = "select publish_datetime, b.chi as media from text_select a left join translation b on a.channel = b.eng where channeltype = 'news' order by publish_datetime asc";
        // $sql_2 = "select a.publish_datetime, c.username as media from text_select a left join t_sinablog c on a.Tid = c.mid where channeltype = 'weibo' order by publish_datetime asc";
        // $sql_3 = "select a.publish_datetime, c.author as media from text_select a left join t_weixin c on a.Tid = c.pid + ';' + c.wid where channeltype = 'weixin' order by publish_datetime asc";
        if ($channel == 0){
            $result = $Model->query($sql_0);
        }
        else if ($channel == 1){
            $result = $Model->query($sql_1);
        }
        // else if ($channel == 2){
            // $result = $Model->query($sql_2);
        // }
        // else if ($channel == 3){
            // $result = $Model->query($sql_3);
        // }
        print json_encode($result);
        
    }
    
    //--  热度分析
    public function api_get_heat(){
        $keyword = $_POST['keyword'];
        $channel = $_POST['channel'];
        $Model = new \Think\Model();
        $sql = "select CrawlTime, channeltype, sum(Treply) as replycount from text_growth a right join text_select c on a.Tid = c.Tid group by CrawlTime, channeltype";
        $result = $Model->query($sql);
        $CrawlTime = $Model->query("select CrawlTime from text_growth group by CrawlTime");
        $result_all = array();
        foreach($CrawlTime as $c){
            $totalcount = 0;
            foreach($result as $r){
                if($c['crawltime']==$r['crawltime']){
                    if($r['channeltype']=='news'){
                        $count = $r['replycount'] * 0.2;
                        $totalcount += $count;
                    }
                    if($r['channeltype']=='weibo'){
                        $count = $r['replycount'] * 0.2;
                        $totalcount += $count;
                    }
                    if($r['channeltype']=='weixin'){
                        $count = $r['replycount'] * 0.2;
                        $totalcount += $count;
                    }
                    if($r['channeltype']=='luntan'){
                        $count = $r['replycount'] * 0.2;
                        $totalcount += $count;
                    }
                    if($r['channeltype']=='tieba'){
                        $count = $r['replycount'] * 0.2;
                        $totalcount += $count;
                    }
                }
            $result_heat = array("crawltime"=>$c['crawltime'], "value"=>$totalcount);
            }
        array_push($result_all, $result_heat);
        }
        print json_encode($result_all);
    }
    
    /*
    public function index(){
        $webRoot = C("WEB_ROOT");
        if(isset($_COOKIE['authKey'])){
            $authKey = $_COOKIE['authKey'];
            if(S($authKey.":groupId") != null){
                $gid = S($authKey.":groupId");
                $groupModel = M("usergroup");
                $queryResult = $groupModel->field("default_page_id")
                ->where("id=".$gid)->limit(1)->select();
                if(count($queryResult) > 0){
                    $redirectUrl = $queryResult[0]["default_page_id"];
                    header('Location: '.C("WEB_ROOT").$redirectUrl);
                }else $this->needLogin();
            }else $this->needLogin();
        }else{
            $this->needLogin();
        }
        exit;
    }
    */
    
    private function needLogin(){
        /*
        $this->assign('startGo','Lungo.Router.section("login-section");');
        $this->display("Public::login");
        */
        header('Location: '.C("WEB_ROOT")."login");
        exit;
    }
    
    private function assignCommon(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $this->assign('userName', S($authKey.":showName"));
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('sitename', C("SITE_NAME"));
        $this->assign('myId', $myId);
        
        $isMobile = 0;
        if(is_mobile()) $isMobile = 1;
        $this->assign('isMobile', $isMobile);
        return $myId;
    }
}
?>