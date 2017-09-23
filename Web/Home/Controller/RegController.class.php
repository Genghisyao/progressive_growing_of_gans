<?php
namespace Home\Controller;
use Think\Controller;

class RegController extends Controller {
    public function _empty($openId){
        $this->assign('webroot',C("WEB_ROOT"));
        $this->assign('openId',$openId);
        $userModel = M("users");
            
        $user = $userModel->where('open_id="'.$openId.'"')->find();
        if($user){
            if($user["login_name"] == ""){
                $this->assign('startGo','Lungo.Router.section("reg-section");ready();');
                $this->assign('wname',$user["nickname"]);
                $this->display("Public::reg");
            }else{
                /*
                if(isset($_COOKIE['openid']) && $_COOKIE['openid'] != ""){
                    $this->assign('startGo','');
                    $this->assign('openId',$openId);
                    $this->assign('userId',$user["login_name"]);
                    $this->assign('wname',$user["nickname"]);
                    $this->display("Public::main_wx");
                }else{*/
                    header('Location: '.C("WEB_ROOT").'stock');
                //}
            }
        }
    }
    
    public function index(){
	    $this->assign('webroot',C("WEB_ROOT"));
	    $this->display();
    }
    
    public function api_reg(){
        LOG::write(json_encode($_POST));
        $user = trim($_POST["user"]);
        $email = trim($_POST["email"]);
        $pass = trim($_POST["pass"]);
        $openid = trim($_POST["openid"]);
        
        if($user == "" || $pass == "" || $openid == "" || $email == ""){
            $result = array ("state"=>104,"title"=>"注册失败","comment"=>"注册失败, 参数缺失");
            print json_encode($result);
            exit;
        }
        
        
        $data = array();
        $data["login_name"] = $user;
        $data["email"] = $email;
        $data["password"] = $pass;
        $data["group_id"] = 50;
        $data["asgn_broker"] = -1;
        $data["orgn_broker"] = -1;
        
        $userModel = M("users");
        $hasUser = $userModel->where('login_name="'.$user.'"')->find();
        
        if($hasUser){
            $result = array ("state"=>104,"title"=>"注册失败","comment"=>"注册失败, 用户名已存在");
            print json_encode($result);
            exit;
        }else{
            $userModel->where('open_id="'.$openid.'"')->save($data);
            
            $userInfo = $userModel->where('open_id="'.$openid.'"')->find();
            if($userInfo){
                $loginAction = A('Login');
                //$authKey = $loginAction->setUserCache($userInfo);
            
                $result = array ("state"=>200,"title"=>"注册成功","comment"=>"注册成功");
                print json_encode($result);
            }
        }
    }
    
    private function isPhone($phone){
        if(preg_match("/1[3458]{1}\d{9}$/", $phone)) return true;
        else return false;
    }
}
?>