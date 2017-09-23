<?php 
namespace Home\Controller;
use Think\Controller;

 class BandipController extends Controller{ 
    function index(){
        $this->assign('error_reason',"(IP 禁止)");
        $this->display("Public:bandip"); 
    }
 } 
 ?>