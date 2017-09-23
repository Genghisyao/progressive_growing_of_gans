<?php
namespace Home\Controller;
use Think\Controller;

class LogoutController extends Controller {
    public function index(){
      $authCookie = cookie('authKey');
	  cookie('authKey',null);
	  clearUserCache($authCookie);
	  
      header('Location: '.C("WEB_ROOT").'login');
    }
    
    public function api_logout(){
      $authCookie = cookie('authKey');
	  cookie('authKey',null);
	  clearUserCache($authCookie);
	  
	  $result = array ("state"=>200,"title"=>"操作成功","comment"=>"登出成功");
	  print json_encode($result);
    }
}
?>