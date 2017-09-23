<?php
namespace Home\Controller;
use Think\Controller;

class DataController extends Controller {
    public function index(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
        $this->assign('webroot',C("WEB_ROOT"));
        $openId = $_COOKIE['openid'];
        
        $this->assign('openId',$openId);
        $this->assign('startGo','');
        $this->display("Public::main_wx");
    }

    public function home(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
        $openId = $_COOKIE['openid'];
        $this->assign('openId',$openId);
        $this->display("WeChat:home");
    }
    
    public function cur(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
        $openId = $_COOKIE['openid'];
        $this->assign('openId',$openId);
        $this->display("WeChat:map");
    }

    public function showtrack(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
        $openId = $_COOKIE['openid'];
        $this->assign('openId',$openId);
        $this->display("WeChat:track");
    }

    public function picture(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
        $openId = $_COOKIE['openid'];
        $this->assign('openId',$openId);
        $this->display("WeChat:lszp");
    }

    public function alarm(){
        if(wxauth(__CLASS__, __FUNCTION__) == false) $this->needLogin();
        $openId = $_COOKIE['openid'];
        $this->assign('openId', $openId);
        $this->display('WeChat:alarm');
    }

//    public function config(){
//        if(wxauth(__CLASS__,__FUNCTION__) == false) $this->needLogin();
//        $this->assign('webroot',C("WEB_ROOT"));
//        $openId = $_COOKIE['openid'];
//
//        $this->assign('openId',$openId);
//        $this->assign('startGo','Lungo.Router.section("config-section");');
//        $this->display("Public::main_wx");
//    }
    
    public function api_toggle_dzwl(){
        LOG::write(json_encode($_POST));
        $openId = $_POST["openid"];
        $command = "dzwl_".$_POST["enable"];
        $cameraAction = A("Camera");
        $cameraData = $cameraAction->getMyCameraInfo($openId);
        
        $msg = "com.baidu.push.Setting with ".$command;
        $cId = $cameraData["bd_channel_id"];
        $uId = $cameraData["bd_user_id"];
        
        $cameraAction->pushToCarRecorder($cId, $uId, $msg);
                                
        print('{"state":200}');
    }
    
    public function test(){
        $t = "dfdDdFfDDfFDdfd";
        print($t[3]);
    }
    
    private function needLogin(){
        $this->display("Public::wx");
        exit;
    }

    //设置警报信息已读
    public function api_set_msg_read(){
        $openId = $_POST["openid"];
        $msgId = $_POST["msgId"];
        $device = getDeviceByOpenid($openId);
        if($device == NULL) {
            print('{"state":104}');
            exit;
        }
        $warningModel = M('warning_msg');
        $warningModel->where('id="%d"', $msgId)->setField('is_read', 1);
    }

    //获取警报信息
    public function api_get_warning_msg(){
        $openId = $_POST["openid"];
        $device = getDeviceByOpenid($openId);
        if($device == NULL) {
            print('{"state":104}');
            exit;
        }
        $warningModel = M('warning_msg');
        $warningData = $warningModel->where('device_id="%s"', $device)->order('add_time desc')->select();
        if(!$warningData){
            print('{"state":100}');
            exit;
        }
        $result = array("state"=>200, "comment"=>$warningData);
        LOG::write(json_encode($result));
        print json_encode($result);
        exit;
    }

    //插入警报信息
    public function api_set_warning_msg(){
        $text = urldecode($_POST["text"]);
        $device = $_POST["device"];
        $warningModel = M('warning_msg');
        $data = array("device_id" => $device, "msg" => $text, "add_time" => date('Y-m-d H:i:s', time()), "is_read" => 0);
        $warningModel->add($data);
    }

    //获取历史轨迹
    public function api_get_track_history(){
        $openId = $_POST["openid"];
        $date = $_POST["chooseDate"];
        LOG::write($date);
        $device = getDeviceByOpenid($openId);
        if($device == NULL) {
            print('{"state":104}');
            exit;
        }
        $trackModel = M('user_track');
        $trackData = $trackModel->where('device_id="%s" AND to_days(t) >= to_days("%s") AND to_days(t) < (to_days("%s") + 1)',$device, $date, $date)->select();
        LOG::write(json_encode($trackData),LOG::DEBUG);
        $result = array ("state"=>200, "comment"=>$trackData, "type"=>"mysql");
        print json_encode($result);
        exit;
    }
    //获取当天轨迹
    public function api_get_track(){
        $openId = $_POST["openid"];
        $device = getDeviceByOpenid($openId);
        if($device == NULL) {
            print('{"state":104}');
            exit;
        }
        $key = "c:".$device;
        $result = getListFromRedis(C('REDIS_HOST'), C('REDIS_PORT'), $key, 0, -1);
        print json_encode($result);
        exit;
    }
    //获取当前位置
    public function api_get_location(){
        $openId = $_POST["openid"];
        $device = getDeviceByOpenid($openId);
        if($device == NULL) {
            print('{"state":104}');
            exit;
        }
        $key = "c:".$device;
        $result = getListFromRedis(C('REDIS_HOST'), C('REDIS_PORT'), $key, -1, -1);
        print json_encode($result);
        exit;

    }
    //
    public function api_check_alarm()
    {
        $openId = $_POST["openid"];
        $alarmData = check_alarm($openId);
        if (!$alarmData) {
            print('{"state":104}');
        } else {
            $result = array("state" => 200, "data" => $alarmData, "type" => "redis");
            LOG::write(json_encode($result),LOG::DEBUG);
            print(json_encode($result));
        }
    }

    // 查看图片详情接口
    public function api_get_picture_details(){
        if(!isset($_POST["id"])){
            $result = array("status"=>104,"comment"=>"picture's id is null!");
            print json_encode($result);
            return;
        }
        $picId = $_POST["id"];
        //$picId = 1;
        $picModel = M("pictures");
        $filedatas = $picModel->where('id="'.$picId.'"')->limit(1)->select();
        if($filedatas){
            $picture = $filedatas[0];
            $result = array("status"=>200,"comment"=>$picture);
            print json_encode($result);
        }
    }
    
    
    public function api_get_history_pic(){
        $openId = $_POST["openid"];
        
        $dir = C('PIC_UPLOAD_FOLDER').$openId;
        
        //$fileList1 = $this->getFile1($dir);
        $fileList = $this->getFile($openId);
        $result = array ("state"=>200, "comment"=>$fileList);
        
        LOG::write(json_encode($result));
        print json_encode($result);
        exit;
    }
    
    //总是获取最新100图片方法
    private function getFile($openId){
        $picModel = M("pictures");
        $filedatas = $picModel->where('open_id="'.$openId.'"')->select();
        $fileArray[] = null;
        
        $i=0;
        if(count($filedatas) < 100){
            for($j = count($filedatas)-1;$j >= 0 ;$j--){
            //获取图片名
            $pic_path = $filedatas[$j]["pic_path"];
            $pic_names = explode("/",$pic_path);
            $pic_name = end($pic_names);//获取数组最后一个元素，即图片名
            //获取图片对应的地址
            $address = $filedatas[$j]["address"];
            $picArray = array($pic_name,$address);//此处数组必须为此格式，因为跟前段排序有关。不能修改！
            $fileArray[$i] = $picArray;
            $i++;
            }
        }else{
            
            LOG::write("count:".count($filedatas));
            for($j = count($filedatas)-1;$j > count($filedatas)-101 ;$j--){
            //获取图片名
            $pic_path = $filedatas[$j]["pic_path"];
            $pic_names = explode("/",$pic_path);
            $pic_name = end($pic_names);//获取数组最后一个元素，即图片名
            //获取图片对应的地址
            $address = $filedatas[$j]["address"];
            $picArray = array($pic_name,$address);//此处数组必须为此格式，因为跟前段排序有关。不能修改！
            $fileArray[$i] = $picArray;
            $i++;
            }
        }
        return $fileArray;  
    }
    //原来获取图片的方法
    private function getFile1($dir) {
        if(!is_dir($dir)) mkdir($dir);
        
        $fileArray[] = null;
        if (false != ($handle = opendir ( $dir ))) {
            $i=0;
            while ( false !== ($file = readdir ( $handle )) ) {
                //去掉"“.”、“..”以及带“.xxx”后缀的文件
                if ($file != "." && $file != ".."&&strpos($file,".")) {
                    $fileArray[$i] = $file;
                    if($i==100){
                        break;
                    }
                    $i++;
                }
            }
            //关闭句柄
            closedir ( $handle );
        }
        return $fileArray;
    }
    
    public function api_login(){
        $user = trim($_POST["user"]);
        $pass = trim($_POST["pass"]);
        
        $userModel = M("users");
        $userInfo = $userModel->where('login_name="'.$user.'" AND password="'.$pass.'"')->find();
        
        if($userInfo){
            $result = array ("state"=>200,"title"=>"登录成功","userId"=>$userInfo["id"],"openId"=>$userInfo["open_id"]);
            print json_encode($result);
        }else{
            $result = array ("state"=>104,"title"=>"登录失败");
            print json_encode($result);
        }
    }
    
    public function api_get_main(){
        if(wxauth(__CLASS__,__FUNCTION__) == false) {
            $result = array ("state"=>104,"title"=>"Fail","comment"=>"请重新登录");
            print json_encode($result);
            exit;
        }
    }
}
























?>