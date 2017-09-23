<?php
namespace Home\Controller;
use Think\Controller;

class LoginController extends Controller {
    public function index(){
	    $this->assign('webroot',C("WEB_ROOT"));
	    $this->assign('sitename',C("SITE_NAME"));
	    $this->assign('domainname',C("SITE_DOMAIN_NAME"));
	    $this->display();
    }
    
    public function api_login(){
        $userName = $_POST["login_name"];
        $password = $_POST["password"];
        $result = array ();
        
        $userModel = M("users");
        
        $userInfo = $userModel->where('login_name="'.$userName.'" and password="'.$password.'" and locked=0')->find();
        if($userInfo){
        
            $userTable = C('DB_PREFIX').'users';
            $groupTable = C('DB_PREFIX').'usergroup';
            $groupTypeTable = C('DB_PREFIX').'usergrouptype';
            
            $userMoreInfo = $userModel->table($userTable." u")
            ->join('LEFT JOIN '.$groupTable.' g on g.id=u.group_id')
            ->field("u.*, g.id as groupId, g.default_page_id as default_page, g.level as level")
            ->where('login_name="'.$userName.'"')->find();
            $authKey = $this->setUserCache($userInfo);
            $result = array ("state"=>200,"title"=>"操作成功","comment"=>"登录成功","authKey"=>$authKey,"goPage"=>$userMoreInfo["default_page"]);
        }else{
            $result = array ("state"=>104,"title"=>"操作结果","comment"=>"用户名或密码不正确.");
        }
        print json_encode($result);
    }
    
    public function api_login_by_login_name(){
        $phone = $_POST["phone"];
        $password = $_POST["password"];
        $result = array ();
        
        $userModel = M("users");
        
        $userInfo = $userModel->where('login_name="'.$phone.'" and password="'.$password.'" and locked=0')->find();
        if($userInfo){
            $userTable = C('DB_PREFIX').'users';
            $groupTable = C('DB_PREFIX').'usergroup';
            $groupTypeTable = C('DB_PREFIX').'usergrouptype';
            
            $userMoreInfo = $userModel->table($userTable." u")
            ->join('LEFT JOIN '.$groupTable.' g on g.id=u.group_id')
            ->field("u.*, g.id as groupId, g.default_page_id as default_page, g.level as level")
            ->where('login_name="'.$phone.'"')->find();
            $authKey = $this->setUserCache($userInfo);
            $result = array ("state"=>200,"title"=>"操作成功","comment"=>"登录成功","authKey"=>$authKey,"goPage"=>$userMoreInfo["default_page"]);
        }else{
            $result = array ("state"=>104,"title"=>"操作结果","comment"=>"用户名或密码不正确.");
        }
        print json_encode($result);
    }
    
    public function setUserCache($userInfo){
        if(S("reference_auth_key:".$userInfo["id"]) != null) {
            $authKey = S("reference_auth_key:".$userInfo["id"]);
        }else{
            $authKey = rand_string();
            S("reference_auth_key:".$userInfo["id"], $authKey, C('CACHE_USER_INFO_SECOND'));
        }
        S($authKey.":userBrokerId", $userInfo["asgn_broker"], C('CACHE_USER_INFO_SECOND'));
        S($authKey.":userId", $userInfo["id"], C('CACHE_USER_INFO_SECOND'));
        S($authKey.":groupId", $userInfo["group_id"], C('CACHE_USER_INFO_SECOND'));
        S($authKey.":userLoginName", $userInfo["login_name"], C('CACHE_USER_INFO_SECOND'));
        S($authKey.":showName", $userInfo["nickname"], C('CACHE_USER_INFO_SECOND'));
        $userGroupModel = M("usergroup");
        $groupInfo = $userGroupModel->where("id=".$userInfo["group_id"])->find();
        if($groupInfo) S($authKey.":level", $groupInfo["level"], C('CACHE_USER_INFO_SECOND'));
        
        return $authKey;
    }
}
?>