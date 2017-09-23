<?php
namespace Home\Controller;
use Think\Controller;

class TestController extends Controller {
    public function index(){
	    //print("here");
	    //phpinfo();

    	//import('ORG.Com.Wechat'); // ThinkPHP/Extend/Library/ORG/Com/Wechat.class.php
		//import('Cache.CacheRedis');// ThinkPHP/Extend/Driver/Cache/CacheRedis.class.php
        
        $startTime = time();
        $redis = new Redis();
        $redis->pconnect('127.0.0.1',6379);
        
        //string 1w/second
        /*
        for($i=0;$i<100000;$i++){
            //$redis->lpush("test","value".$i);
            $curValue = $redis->lrange("test", 0, 0);
        }
        */
        $endTime = time();
        $allTime = $endTime - $startTime;
		
		LOG::write($_GET["d"],DEBUG);
        
     	//$redisObj = new CacheRedis();
		//$name = 'foo';
		//print($redisObj->get($name));
        //$this->assign('userName', 'Team');
        $this->assign('webroot',C("WEB_ROOT"));
	    $this->display();
		
    }
	
	public function actionhere(){
	    print("actionhere");
	}
    
    public function redis(){
        
        $redis = new Redis();
    }
    
    public function aes(){
        Vendor('Carslink.AES');
        $aes = new AES(true);// 把加密后的字符串按十六进制进行存储
        //$aes = new AES(true,true);// 带有调试信息且加密字符串按十六进制存储
        $key = "1234567890123456";// 密钥
        $keys = $aes->makeKey($key);
        foreach($keys as $k => $v){
            print($v." ");
        }
        print("<br />");
        $encode = "1387127259:13912345678:000123456";// 被加密的字符串
        $ct = $aes->encryptString($encode, $keys);
        $startTime = time();
        print($startTime."<br>");
        for($i=0;$i<10;$i++){
          //$ct = $aes->encryptString($encode, $keys);
          $cpt = $aes->decryptString($ct, $keys);
        }
        echo "encode = ".$ct." count:".strlen($ct)."<br>";
        echo "decode = ".$cpt."<br>";
        print("time: ".(time()-$startTime));
    }
    
    public function json(){
        $jsonStr = '{"a":"test","e":-12.50}';
        $j = json_decode($jsonStr,true);
        print($j["e"]);
    }
    
    public function mem(){
        $memcached = new CacheMemcached();
        $data = array(
            'key1' => 'value1',
            'key2' => 'value2',
            'key3' => 'value3',
            );
        $memcached->setMulti($data,60);
        
        $key = array('key1','key2','key3','key4');
        
        foreach($memcached->getMulti($key) as $key => $value)
        print($key."=>".$value."<br />");
        
        $memcached->setMulti($data,60);
        
        /*
    	$startTime = time();
        $authKey = $_COOKIE['authKey'];
        $eCount = 0;
        for($i=0;$i<200000;$i++){
        	$id = S($authKey.":userId");
        	if($id == "" || $id == null) $eCount ++;
        }
        print("error count is ".$eCount." in $i operations. $id time: ".(time()-$startTime));
        */
    }
    
    public function auth(){
        print $_COOKIE['authKey'];
    }
    
    public function submit(){
        $obj["GET"] = $_GET;
        $obj["POST"] = $_POST;
        $obj["state"] = 200;
		$resultStr = json_encode($obj);
		LOG::write($resultStr,LOG::DEBUG);
        print $resultStr;
    }
    
    public function mem_key(){
        $string = "";
        $time = mktime(0, 0, 0, 1, 1, date('Y',time()));
        $startTime = $time;
        print(time() - $startTime."<br />");
        for($i=0;$i<400;$i++){
            $time = mktime(date('G',$time), date('i',$time), date('s',$time)+30, date('d',$time), date('m',$time), date('Y',$time));
            $addTime = $time - $startTime;
            $string = $string.$time.",";
            //$string = $string.$time.",";
        }
        //$string = "array(".$string.")";
        S("test:value:length",$string,600);
        //print(S("test:value:length"));
        $testarray = array();
        eval('$testarray=array('.S("test:value:length").');');
        print(count($testarray));
        print($testarray[count($testarray)-1]);
    }
    
    public function rpc(){
        require('xmlrpc.inc.php');
        $client = new xmlrpc_client('/', '114.215.236.193', '8658');
        $client->setDebug(0);
        $client->request_charset_encoding='utf-8';
        $client->debug=true;
        
        //print("client: ".var_dump($client)."<br /><br />");
        
        $data = date('Y-m-d H:i:s',time());
        
        try {
            //$param = new xmlrpcmsg('getAllNodeStatus', array(php_xmlrpc_encode($data)));
            $param = new xmlrpcmsg('getAllNodeStatus');
            $result = $client->send($param);
            
            //var_dump($result);
            
            if(!$result->faultCode()) {
                $val = $result->value();
                //print(php_xmlrpc_decode($val));
                
                foreach(php_xmlrpc_decode($val) as $key => $value){
                    print $key." => ".json_encode($value)."<br />";
                }
                
            } else {
                print("got faultCode ".$result->faultCode());
            }
        } catch (Exception $e) {
            //var_dump($e);
        }
        
        //print("OK");
    }
}
?>