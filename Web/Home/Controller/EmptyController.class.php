<?php 
namespace Home\Controller;
use Think\Controller;

 class EmptyController extends Controller{ 
    function _empty(){ 
        header("HTTP/1.0 404 Not Found");//使HTTP返回404状态码 
        $this->assign('webroot',C("WEB_ROOT"));
        $this->assign('error_reason',"(模块不存在)");
        $this->display("Public:error-404"); 
    }
 } 
 ?>