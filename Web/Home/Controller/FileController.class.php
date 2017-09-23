<?php
namespace Home\Controller;
use Think\Controller;

class FileController extends Controller {
    public function index(){
         $this->display();
    }
    
    public function connect(){
        define("IN_ADMIN", 1);//重要，定义一个常量，在插件的PHP入口文件中验证，防止非法访问。
        
        // Documentation for connector options:
        // https://github.com/Studio-42/elFinder/wiki/Connector-configuration-options
        $opts = array(
            // 'debug' => true,
            'roots' => array(
                array(
                    'driver'        => 'LocalFileSystem',   // driver for accessing file system (REQUIRED)
                    'path'          => './upload/我的文件/',         // path to files (REQUIRED)
                    'URL'           => dirname($_SERVER['PHP_SELF']) . './upload/我的文件/', // URL to files (REQUIRED)
                    'accessControl' => 'access'             // disable and hide dot starting files (OPTIONAL)
                )
            )
        );
        include './elFinder/connector.minimal.php';//包含elfinder自带php接口的入口文件
    }
}
?>