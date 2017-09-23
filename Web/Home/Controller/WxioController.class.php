<?php
namespace Home\Controller;
use Think\Controller;

define("TOKEN", C('TOKEN'));
define("APPID", C('APPID'));
define("APPSECRET", C('APPSECRET'));
define("PUBLIC_OPEN_ID", C('PUBLIC_OPEN_ID'));

// logs: \www\wxpub\Runtime\Logs\*.log
// pass openid:
// https://open.weixin.qq.com/connect/oauth2/authorize?
// appid=wx167976eafa565cd1&redirect_uri=http%3A%2F%2Fweixin.carslink.net%2Fdata%2Fpicture&
// response_type=code&scope=snsapi_base&state=STATE#wechat_redirect

// public function receive(){
//    $openId = $_COOKIE['openid'];
// }

// Reply a message:
// $weObj->text($repStr)->reply();
// $news = array(
//     array(
//         'Title'=>'您已成功开启电子围栏',
//         'PicUrl'=>'http://restapi.amap.com/v3/pic.jpg',
//         'Url'=>'https://open.weixin.qq.com/connect/oauth2/authorize?appid='.APPID.'&
//                 redirect_uri=http%3A%2F%2Fweixin.carslink.net%2Fdata%2Falarm&
//                 response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
//     )
// );
// $weObj->news($news)->reply();

// Title Description Content 均可直接换行

// 临时二维码时为32位非0整型，永久二维码时最大值为1000（目前参数只支持1--100000）
// 获取二维码ticket后，开发者可用ticket换取二维码图片。请注意，本接口无须登录态即可调用。
// https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=TICKET

class WxioController extends Controller {
    /*-----------------------------------------------------------------------------------------------------------*/
    /* 默认入口 */
    public function index(){
        if(isset($_GET["echostr"])){
            print($_GET["echostr"]);
            exit;
        }
        
        $options = array(
                 'token'=> TOKEN, //填写你设定的key
                 'appid'=> APPID, //填写高级调用功能的app id
                 'appsecret'=> APPSECRET, //填写高级调用功能的密钥
             );
        import('ORG.Com.Wechat'); // ThinkPHP/Extend/Library/ORG/Com/Wechat.class.php
        
        $weObj = new Wechat($options);
        
        $wholeMsgJson = $weObj->json_encode($weObj->getRev());
        LOG::write("info from client is ".$wholeMsgJson,LOG::DEBUG);

        //1. disable $weObj->valid(), 由于该函数工作不是很正常，具体原因仍需调查        
        //2. 腾讯服务器发过来的'地理位置信息(接收普通消息)'没有带signature,timestemp,nonce, 
        //无法通过Wechat::checkSignature,所以在这里特别绕开    
        /*
        if ( $weObj->getRev()->getRevType() != Wechat::MSGTYPE_LOCATION) {
            $weObj->valid();
        }
        */
        
        $type = $weObj->getRev()->getRevType();    
        $openId = $weObj->getRev()->getRevFrom();
        $toUserName = $weObj->getRev()->getRevTo();
        $dateline = $weObj->getRev()->getRevCtime();
        $nowtime = date('H:i:s',$dateline); 
        LOG::write("msgType is ".$type,LOG::DEBUG);

        
        switch($type) {
            case Wechat::MSGTYPE_TEXT:
                $contentFromUser = $weObj->getRev()->getRevContent();
                $userModel = M("user_info");
                $userData = $userModel->where('openid = "'.$openId.'"')->select();
                $userDataLine = $userData[0];
                $nickName = $userDataLine['nickname'];    
                // LOG::write("phpInfo is ".json_encode(phpinfo()),LOG::DEBUG);
                $repStr = 'Hi '.$nickName.', 你发送过来的信息是:
                          '.$contentFromUser.'.';
                //$weObj->text($repStr)->reply();
                $news = array(
                             array(
                                 'Title'=>'文章标题',
                                 'Description'=>
'1. 第一行
2. 第二行',
                                 'PicUrl'=>'',
                                 'Url'=>''
                             ),
                             array(
                                 'Title'=>
'1. 标题第一行
2. 标题第二行',
                                 'Description'=>
'1. 第一行
2. 第二行',
                                 'PicUrl'=>'',
                                 'Url'=>''
                             )
                         );
                $weObj->news($news)->reply();
                break;
            case Wechat::MSGTYPE_LOCATION:
                LOG::write("on MSGTYPE_LOCATION",LOG::DEBUG);
                $arrayGeo = $weObj->getRevGeo();
                $result = json_encode($arrayGeo);

                $lat = $arrayGeo['x'];
                $lng = $arrayGeo['y'];
                LOG::write("lat: ".$lat." lng: ".$lng, LOG::DEBUG);
                break;
            case Wechat::MSGTYPE_EVENT:
                $eventArr = $weObj->getRev()->getRevEvent();
                $event = $eventArr['event'];
                LOG::write("case Wechat::MSGTYPE_EVENT - Event:"
                           .$eventArr['event'].", Key:"
                           .$eventArr['key'],
                           LOG::DEBUG);
                           
                switch($event) {
                    case Wechat::MSGTYPE_EVENT_CLICK:
                        if (isset($eventArr['key'])) {
                            $key = $eventArr['key'];
                            if ($key == "shoot") {
                            }else if($key == "incar"){
                            }else if($key == "reg"){
                            }else if($key == "product"){
                            }else if($key == "alarm"){
                            }
                        } else {
                            LOG::write("Wechat::MSGTYPE_EVENT_CLICK - error",LOG::DEBUG);
                        }
                        break;
                        
                    case Wechat::MSGTYPE_EVENT_LOCATION:
                        LOG::write("on MSGTYPE_EVENT_LOCATION",LOG::DEBUG);
                        $Geo = $weObj->getRev()->getRevGeoEvent();
                        LOG::write("Geo is:".$weObj->json_encode($Geo),LOG::DEBUG);
                        break;
                        
                    case Wechat::MSGTYPE_EVENT_SCAN:
                        if (isset($eventArr['key'])) {
                            $key =$eventArr['key'];
                            $weObj->text($key)->reply();
                        } else {
                            LOG::write("Wechat::MSGTYPE_EVENT_SCAN - error",LOG::DEBUG);
                        }
                        break;
                    case Wechat::MSGTYPE_EVENT_subscribe:
                        $userModel = M("users");
                        $userData = array();
                        $userData["open_id"] = $openId;
                        $userData["open_id_public"] = $toUserName;
                        $userData["group_id"] = 50;
                        //$userModel->add($userData);

                        $userInfoArray = $weObj->getUserInfo($openId);
                        unset($userInfoArray["openid"]); //remove element of $userInfoArray["openid"]
                        $result = array_merge((array)$userData, (array)$userInfoArray);
                        
                        LOG::write("info of user is ".$weObj->json_encode($result),LOG::DEBUG);
                        //$userModel = M("user_info");
                        $userModel->add($result);
                        //reg
                        if (isset($eventArr['key'])) {
                            $key = $eventArr['key'];
                            $weObj->text($key)->reply();
                        }
                        
                        $news = array(
                            array(
                                'Title'=>'米蛙车载智能平台-即录仪',
                                'PicUrl'=>'http://weixin.carslink.net/assets/images/logo-miwalk.jpg',
                                'Url'=>C('PRODUCT_URL')
                            )
                        );
                        
                        $weObj->news($news)->reply();
                        //$weObj->text('欢迎关注我们! 请点击<a href="http://weixin.carslink.net/reg/'.$userData["open_id"].'"> 这里 </a> 注册微安防账号.')->reply();
                        break;
                    case Wechat::MSGTYPE_EVENT_unsubscribe:
                        $userModel = M("users");
                        $userModel->where('open_id = "'.$openId.'"')->delete();
                        LOG::write("Wechat::MSGTYPE_EVENT_unsubscribe - after delete 0",LOG::DEBUG);
                        break;    
                    default:
                        $weObj->text("unreconized event")->reply();
                }                                        
                break;
            case Wechat::MSGTYPE_IMAGE:
                break;
            default:
                $weObj->text("help info")->reply();
        }
        //$this->send();
    
    } // func index
    
    /*****
    * http://112.124.47.197/blank_project/wxio/api_get_qr_ticket/13579/1
    * getQRCode($scene_id,$type=0,$expire=1800)
    * @param int $type 0:临时二维码；1:永久二维码(此时expire参数无效)
	* @param int $expire 临时二维码有效期，最大为1800秒
	* @return array('ticket'=>'qrcode字串','expire_seconds'=>1800)
    * http://weixin.qq.com/q/BXSj-X3mf4YGSy9UQVra is final result
	*/
    
    public function api_get_qr_ticket() {
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat');
        $weObj = new Wechat($options);

        $key = $_GET["_URL_"][2];
        
        $result = array();
        if(isset($_GET["_URL_"][3])){
            $type = $_GET["_URL_"][3];
            $result = $weObj->getQRCode($key, $type);
        }else $result = $weObj->getQRCode($key);

        print(json_encode($result));
    }
    
    /*-----------------------------------------------------------------------------------------------------------*/
    /* 测试代码主动发送信息给用户
    * http://weixin.carslink.net/wxio/send
    */    
    public function send() {
        ///*
        $fromUserName = "oB2qat8uDjwTeEn4b6E_Wtbumz9M";
        $articles = array( 
            array(
                'Title'=>'航班劫机者被捕',
                'Description'=>'埃塞航班劫机者被捕 或系寻求庇护飞行员',
                'PicUrl'=>'http://photocdn.sohu.com/20140217/Img395138958.jpg',
                'Url'=>'http://news.sohu.com/20140217/n395138957.shtml?adsid=1'
            )
        );    
        $this->api_sendMsgToCustomer_news($fromUserName,$articles);
        
        $text = "来自公众帐号主动发送的文字消息!";
        $this->api_sendMsgToCustomer_text($fromUserName, $text);
    }
    
    /*-----------------------------------------------------------------------------------------------------------*/    
    /* 删除微信菜单
    *
    */    
    public function api_deleteMenu() {
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat'); 
        $weObj = new Wechat($options);        
        
        $weObj->deleteMenu();
    }    
    
    /*-----------------------------------------------------------------------------------------------------------*/
    /* 获取微信菜单
    *    
    */    
    public function api_getMenu() {
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat'); 
         $weObj = new Wechat($options);        
        
        $result = $weObj->getMenu();
        if ($result) {
            //$jsonMenu = json_decode($result,true);
            return $result;
        }
        return false;
    }

    /*----------------------------------------------------------------------------------------------*/
    /* 创建微信菜单
    * $newMenu =  array (
    *     "button" => array (
    *         array(    "type" => "click", "name" => "今日歌曲", "key"  => "V1001_TODAY_MUSIC"),
    *         array( "type" => "click", "name" => "歌手简介", "key"  => "V1001_TODAY_SINGER"),
    *         array( "name"  => "菜单",
    *               "sub_button"  => array (
    *                    array ( "type" => "view", "name" => "搜索", "url"  => "http://www.baidu.com/"),
    *                    array ( "type" => "click","name" => "赞一下我们", "key"  => "V1001_GOOD" )
    *                )
    *           )
    *     )
    * );    
    */    
    public function api_createMenu($newMenu) {
        LOG::write("api_createMenu - entrance",LOG::DEBUG);
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat'); 
         $weObj = new Wechat($options);        
        
        LOG::write("JSON of newmenu is ".json_encode($newMenu),LOG::DEBUG);
        $result = $weObj->createMenu($newMenu);
        if ($result) {
            //$jsonMenu = json_decode($result,true);
            return $result;
        }
        return false;
    }
    
    public function api_sendPicToUser($openId, $path, $id){
        $picAddr = 'http://weixin.carslink.net/'.$path.'?t='.time();
        $articles = array( 
            array(
                'title'=>'您所拍摄的相片',
                'description'=>'',
                'picurl'=>$picAddr,
                'url'=>'https://open.weixin.qq.com/connect/oauth2/authorize?appid='.APPID.'&redirect_uri=http%3A%2F%2Fweixin.carslink.net%2FWeChat%2Fyztpxx%2F?id='.$id.'&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
            )
        );
        $this->api_sendMsgToCustomer_news($openId, $articles);
    }
    
    /*-----------------------------------------------------------------------------------------------------------*/
    /* 主动发送图文信息给用户
    *  图文信息
    *  如有问题, 将Title,Description,PicUrl,Url等全部改成小写. 原因未明
    *    $articles = array( 
    *        array(
    *            'Title'=>'航班劫机者被捕',
    *            'Description'=>'埃塞航班劫机者被捕 或系寻求庇护飞行员',
    *            'PicUrl'=>'http://photocdn.sohu.com/20140217/Img395138958.jpg',
    *            'Url'=>'http://news.sohu.com/20140217/n395138957.shtml?adsid=1'
    *        )
    *    );
    */    
    public function api_sendMsgToCustomer_news($toUser, $articles) {
        LOG::write("api_sendMsgToCustomer_news - entrance",LOG::DEBUG);
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat'); 
         $weObj = new Wechat($options);        
    
        $msgToUser = array('touser' => $toUser, 'msgtype' => Wechat::MSGTYPE_NEWS, 'news' => array ('articles' => $articles ));
        
        $result = $weObj->json_encode($msgToUser);
        //$result = json_encode($msgToUser);
        LOG::write("api_sendMsgToCustomer_news - MSG is ".$result,LOG::DEBUG);
        $weObj->sendCustomMessage($msgToUser);
    }    
    
    /*-----------------------------------------------------------------------------------------------------------*/
    /* 主动发送文字信息给用户
    *  文字信息
    *  $text = "来自公众帐号主动发送的文字消息!"
    */    
    public function api_sendMsgToCustomer_text($toUser, $text) {
        LOG::write("api_sendMsgToCustomer_text - entrance",LOG::DEBUG);
        $options = array('token' => TOKEN,'appid' => APPID, 'appsecret' => APPSECRET);
        import('ORG.Com.Wechat'); 
        $weObj = new Wechat($options);
            
        $msgToUser = array ('touser' => $toUser,'msgtype' => Wechat::MSGTYPE_TEXT,'text' => array('content' => $text));        
        $result = $weObj->json_encode($msgToUser);
        LOG::write("api_sendMsgToCustomer_text - msg is ".$result,LOG::DEBUG);
        
        $weObj->sendCustomMessage($msgToUser);
    }    
    
}
?>