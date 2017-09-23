<?php
function wxauth($className,$functionName){
    if((isset($_COOKIE['openid']) && $_COOKIE['openid'] != "") 
      || (isset($_POST['openid']) && $_POST['openid'] != "")){
        $openId = $_COOKIE['openid'];
        if($openId == "") $openId = $_POST['openid'];
        \Think\Log::write($openId);
        $userModel = M("users");
        $userInfo = $userModel->where('open_id="'.$openId.'" AND login_name!=""')->find();
        if($userInfo) return true;
        else return false;
    } else return false;
}

function auth($className,$functionName){
    checkBandedIp();
    $className = str_replace("\\", "_", $className);
    $logInPass = false;
    $checkPass = false;
    if(!isset($_COOKIE['authKey'])) needlogin($functionName);
    $authKey = $_COOKIE['authKey'];
    
    if($authKey != "" && checkCacheCompletion($authKey)) $logInPass = true;
    else if($authKey != "") {
        clearUserCache($authKey);
        recordBadVisite();
    }
    
    $groupId = S($authKey.":groupId");
    if($logInPass == true && $groupId != ""){
        
        //\Think\Log::record("log content====".constant("APP_DEBUG"),\Think\Log::DEBUG);
        //\Think\Log::save();
        
        if(constant("APP_DEBUG") == true){
          $apiModel = M("controller_api");
          $apiLines = $apiModel->where('function_name="'.$className.":".$functionName.'"')->select();
          if(count($apiLines) == 0){
              $data["function_name"] = $className.":".$functionName;
              if(strpos($data["function_name"],":api_") != false){
                  $data["show_in_left_menu"] = 0;
              }
              $apiModel->add($data);
          }
        }
        
        // TODO: 因为现在没有用户组管理页面，不能刷新权限，所以这里加了  || true 强制刷新
        if(S($className.":".$functionName.":".$groupId) == null || true) refreshGroupPrivilegeCache($groupId);
        
        $cacheKey = $className.":".$functionName.":".$groupId;
        
        $cachePrivilege = S($cacheKey);
        if($cachePrivilege != "0") $checkPass = true;
        if($cachePrivilege != "0" && $cachePrivilege != "1") return $cachePrivilege;  // for side menu
    }
    /*
    if($groupId == 1){
        $logInPass = true;
        $checkPass = true;
    }
    */
    if($logInPass == false || $checkPass == false) needlogin($functionName);
}

function account_list(){
    $accModel  = M("deploy");
    $accList = $accModel->order("id")->select();
    return $accList;
}

function getAccInfo($acc){
    $accModel  = M("deploy");
    $accObj = $accModel->where('account_id="'.$acc.'"')->find();
    return $accObj;
}

function is_mobile(){
    // returns true if one of the specified mobile browsers is detected
    $regex_match="/(nokia|iphone|android|motorola|^mot\-|softbank|foma|docomo|kddi|up\.browser|up\.link|";
    $regex_match.="htc|dopod|blazer|netfront|helio|hosin|huawei|novarra|CoolPad|webos|techfaith|palmsource|";
    $regex_match.="blackberry|alcatel|amoi|ktouch|nexian|samsung|^sam\-|s[cg]h|^lge|ericsson|philips|sagem|wellcom|bunjalloo|maui|";
    $regex_match.="symbian|smartphone|midp|wap|phone|windows ce|iemobile|^spice|^bird|^zte\-|longcos|pantech|gionee|^sie\-|portalmmm|";
    $regex_match.="jig\s browser|hiptop|^ucweb|^benq|haier|^lct|opera\s*mobi|opera\*mini|320x320|240x320|176x220";
    $regex_match.=")/i";
    return isset($_SERVER['HTTP_X_WAP_PROFILE']) or isset($_SERVER['HTTP_PROFILE']) or preg_match($regex_match, strtolower($_SERVER['HTTP_USER_AGENT']));
}

function http_post($url, $data){
    $data = http_build_query($data);
    $opts = array (
        'http' => array (
            'method' => 'POST',
            'header'=> "Content-type: application/x-www-form-urlencoded\r\n" .
            "Content-Length: " . strlen($data) . "\r\n",
            'content' => $data
        )
    );
    $context = stream_context_create($opts);
    $result = file_get_contents($url, false, $context);
    return $result;
}

function http_get($url){
    $oCurl = curl_init();
    if(stripos($url,"https://")!==FALSE){
        curl_setopt($oCurl, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($oCurl, CURLOPT_SSL_VERIFYHOST, FALSE);
    }
    curl_setopt($oCurl, CURLOPT_URL, $url);
    curl_setopt($oCurl, CURLOPT_RETURNTRANSFER, 1 );
    $sContent = curl_exec($oCurl);
    $aStatus = curl_getinfo($oCurl);
    curl_close($oCurl);    
    if(intval($aStatus["http_code"])==200){
        return $sContent;
    }else{
        return false;
    }
}

function checkCacheCompletion($authKey){
    if(S($authKey.":userId") == null) return false;
    //if(S($authKey.":groupTypeId") == null) return false;
    if(S($authKey.":groupId") == null) return false;
    //if(S($authKey.":userLoginName") == null) return false;
    //if(S($authKey.":userWeixinName") == null) return false;
    //if(S($authKey.":boxId") == null) return false;
    return true;
}

function clearUserCache($authKey){
    S($authKey.":userId",null);
    S($authKey.":groupTypeId",null);
    S($authKey.":groupId",null);
    S($authKey.":userLoginName",null);
    S($authKey.":userNickName",null);
    S($authKey.":boxId",null);
    S($authKey.":infoCompletion",null);
}

function refreshGroupPrivilegeCache($groupId){
    $apiModel = M("controller_api");
    $apiLines = $apiModel->select();
    foreach($apiLines as $apiLine){
        S($apiLine["function_name"].":".$groupId, "0");  // no privilege
    }
    
    \Think\Log::write("here 0");
    
    $privilegeModel = M("group_privileges");
    $privilegeTable = C('DB_PREFIX').'group_privileges';
    $apiTable = C('DB_PREFIX').'controller_api';
    $apiLines = $privilegeModel->table($privilegeTable." p")
    ->join('LEFT JOIN '.$apiTable.' a on a.id=p.api_id')
    ->field("a.function_name as api_name")
    ->where('p.group_id='.$groupId)->select();
    
    foreach($apiLines as $apiLine){
        \Think\Log::write("here: ". $apiLine);
        
        if(strpos($apiLine["api_name"], ":api_") == false){
            $menuStr = getSideMenu($groupId, $apiLine["api_name"]);
            S($apiLine["api_name"].":".$groupId, $menuStr);    // has side menu
        }else S($apiLine["api_name"].":".$groupId, "1");  // has privilege but no side menu
    }
}

function getSideMenu($groupId, $api_name){
    //print("buildSideMenu<br />");
    $privilegeModel = M("group_privileges");
    $privilegeTable = C('DB_PREFIX').'group_privileges';
    $apiTable = C('DB_PREFIX').'controller_api';
    $allPrivileges = $privilegeModel->table($privilegeTable." p")
    ->join('LEFT JOIN '.$apiTable.' a on a.id=p.api_id')
    ->field("a.id as id, a.function_name as fname, a.show_name as sname,a.parent_id as pid")
    ->where('p.group_id='.$groupId.' and a.show_in_left_menu=1')
    ->order('a.sequence_level asc')
    ->select();
    
    list($dataStruct, $cActive) = getChild($allPrivileges, 0, $api_name);
    //$dataStruct = getChild($allPrivileges, 0, $api_name);
    
    return buildMenu($dataStruct);
}

function buildMenu($dataStruct){
    $htmlStr = "";
    foreach ($dataStruct as $data){
        if($data["active"] == true && count($data["child"]) > 0) $htmlStr .= '<li class="active open">';
        else if($data["active"] == true) $htmlStr .= '<li class="active">';
        else $htmlStr .= "<li>";
        //print( $htmlStr.$data["id"]."<br />");
        //$fname = $data["child"];
        $link = '<a href="#" class="dropdown-toggle">';
        if(count($data["child"]) == 0){
            $url = mb_strtolower(preg_replace("/.*_(.+)Controller:/","$1/",$data["fname"]));
            if($url != "#") $url = C("WEB_ROOT").$url;
            $link = '<a href="'.$url.'">';
        }
        $htmlStr .= $link.'<i class="icon-dashboard"></i><span class="menu-text"> '.$data["sname"].' </span>';
        if(count($data["child"]) > 0) {
            $htmlStr .= '<b class="arrow icon-angle-down"></b></a>';
            $htmlStr .= '<ul class="submenu">';
            $htmlStr .= buildMenu($data["child"]);
            $htmlStr .= '</ul>';
        }else $htmlStr .= '</a>';
        $htmlStr .= "</li>";
    }
    return $htmlStr;
}

function getChild($allPrivileges, $id, $api_name){
    $result = array();
    $pActive = false;
     for($i=0;$i<count($allPrivileges);$i++){
        //print($id." ".$allPrivileges[$i]["pid"]."<br />");
        if($allPrivileges[$i]["pid"] == $id){
            $active = false;
            if(mb_strtolower($allPrivileges[$i]["fname"]) == mb_strtolower($api_name)) $active = true;
            $sname = $allPrivileges[$i]["fname"];
            if($allPrivileges[$i]["sname"] != null) $sname = $allPrivileges[$i]["sname"];
            list($child, $cActive) = getChild($allPrivileges, $allPrivileges[$i]["id"], $api_name);
            if($cActive == true || $active == true) {
                $pActive = true;
                $active = true;
            }
            $result[] = array("id"=>$allPrivileges[$i]["id"],"sname"=>$sname,"fname"=>$allPrivileges[$i]["fname"],"active"=>$active,"child"=>$child);
        }
     }
     $returnList = array();
     $returnList[] = $result;
     $returnList[] = $pActive;
     return $returnList;
}

function needlogin($functionName){
    //header('Location: '.'/login');    // php method
    //redirect("/login", 0, "need log in..."); // thinkphp method
    if (substr($functionName, 0, 4) != "api_") header('Location: '.C("WEB_ROOT").'login');
    else {
        $result = array ("state"=>104,"title"=>"验证错误","comment"=>"无操作权限.");
        print(json_encode($result));
    }
    exit;
}

function recordBadVisite(){
    $curIp = getIp();
    if(S("bad_visit_ip_".$curIp) != null){
        $curCount = S("bad_visit_ip_".$curIp)+1;
        S("bad_visit_ip_".$curIp, $curCount."",21600);
        if(S("bad_visit_ip_".$curIp) >= 30) S("banded_ip_".$curIp,"1",21600);
    }else{
        S("bad_visit_ip_".$curIp,"1",21600);
    }
}

function checkBandedIp(){
    if(S("banded_ip_".getIp()) != null){
      header('Location: '.C("WEB_ROOT").'bandip');
      exit;
    }
}

function getIp(){
    if(!empty($_SERVER["HTTP_CLIENT_IP"])){
      $cip = $_SERVER["HTTP_CLIENT_IP"];
    }
    elseif(!empty($_SERVER["HTTP_X_FORWARDED_FOR"])){
      $cip = $_SERVER["HTTP_X_FORWARDED_FOR"];
    }
    elseif(!empty($_SERVER["REMOTE_ADDR"])){
      $cip = $_SERVER["REMOTE_ADDR"];
    }
    else{
      $cip = null;
    }
    return $cip;
}

function startTimestampByDay($timestamp){
    return mktime(0, 0, 0, date('d',$timestamp), date('m',$timestamp), date('Y',$timestamp));
}

function msubstr($str, $start=0, $length, $charset="utf-8", $suffix=true) {
    if(function_exists("mb_substr"))
        $slice = mb_substr($str, $start, $length, $charset);
    elseif(function_exists('iconv_substr')) {
        $slice = iconv_substr($str,$start,$length,$charset);
        if(false === $slice) {
            $slice = '';
        }
    }else{
        $re['utf-8']   = "/[\x01-\x7f]|[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xff][\x80-\xbf]{3}/";
        $re['gb2312'] = "/[\x01-\x7f]|[\xb0-\xf7][\xa0-\xfe]/";
        $re['gbk']    = "/[\x01-\x7f]|[\x81-\xfe][\x40-\xfe]/";
        $re['big5']   = "/[\x01-\x7f]|[\x81-\xfe]([\x40-\x7e]|\xa1-\xfe])/";
        preg_match_all($re[$charset], $str, $match);
        $slice = join("",array_slice($match[0], $start, $length));
    }
    return $suffix ? $slice.'...' : $slice;
}

/**
 * 产生随机字串，可用来自动生成密码 默认长度6位 字母和数字混合
 * @param string $len 长度
 * @param string $type 字串类型
 * 0 字母 1 数字 其它 混合
 * @param string $addChars 额外字符
 * @return string
 */
function rand_string($len=12,$type=0,$addChars='') {
    $str ='';
    switch($type) {
        case 0:
            $chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.$addChars;
            break;
        case 1:
            $chars= str_repeat('0123456789',3);
            break;
        case 2:
            $chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ'.$addChars;
            break;
        case 3:
            $chars='abcdefghijklmnopqrstuvwxyz'.$addChars;
            break;
        case 4:
            $chars = "".$addChars;
            break;
        default :
            // 默认去掉了容易混淆的字符oOLl和数字01，要添加请使用addChars参数
            $chars='ABCDEFGHIJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'.$addChars;
            break;
    }
    if($len>10 ) {//位数过长重复字符串一定次数
        $chars= $type==1? str_repeat($chars,$len) : str_repeat($chars,5);
    }
    if($type!=4) {
        $chars   =   str_shuffle($chars);
        $str     =   substr($chars,0,$len);
    }else{
        // 中文随机字
        for($i=0;$i<$len;$i++){
          $str.= msubstr($chars, floor(mt_rand(0,mb_strlen($chars,'utf-8')-1)),1);
        }
    }
    return $str;
}

/*
* 发送邮件
* @param $to string
* @param $title string
* @param $content string
* @return bool
* */
function sendMail($to, $title, $content){    
    Vendor('PHPMailer.PHPMailerAutoload');   
    $mail = new PHPMailer(); //实例化
    $mail->IsSMTP(); // 启用SMTP
    $mail->port=25;//端口号
    $mail->Host='smtp.exmail.qq.com'; //smtp服务器的名称
    $mail->SMTPAuth = true; //启用smtp认证        
    $mail->Password = 'Desktop4you' ; //邮箱密码
    $mail->Username ='john@naswork.com'; //你的邮箱名
    $mail->From ='john@naswork.com';//发件人地址
    $mail->FromName ='john@naswork.com'; //发件人姓名
    $mail->AddAddress($to);//收件人
    $mail->WordWrap = 50; //设置每行字符长度
    $mail->IsHTML=true; // 是否HTML格式邮件
    $mail->CharSet='utf-8'; //设置邮件编码
    $mail->Subject =$title; //邮件主题
    $mail->Body = $content; //邮件内容
    $mail->AltBody="text/html";
    return($mail->Send());
    }

?>
