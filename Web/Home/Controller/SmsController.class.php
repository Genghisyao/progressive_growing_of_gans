<?php
namespace Home\Controller;
use Think\Controller;

class SmsController extends Controller {
    public function index(){
        $myId = $this->assignCommon();
        if(is_mobile()){
            $user_agent = $_SERVER['HTTP_USER_AGENT'];
            $isInWx = 0;
            if (strpos($user_agent, 'MicroMessenger') === false) {
            } else {
                $isInWx = 1;
            }
            $this->assign('isInWx',$isInWx);
            $this->display("index_mobile");
        }else
            $this->display();
    }
    
    public function test(){
        $interfaceId = 'sms178';
        $countStr = trim(exec('ps -ef | grep "trigerGetSmsStatus '.$interfaceId.'" | grep -v grep | wc -l'));
        print $countStr;
        if($countStr == 0){
            print "here<br />";
            $str = 'nohup python ./python/sms.py trigerGetSmsStatus '.$interfaceId.' >/dev/null 2>&1 &';
            print $str;
            print system($str);
        }
    }
    
    public function batchadv(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        $this->display();
    }
    
    public function reply_a(){
        \Think\Log::write("GET: ".json_encode($_GET));
        \Think\Log::write("POST: ".json_encode($_POST));
        print "0";
    }
    
    public function status_a(){
        \Think\Log::write("GET: ".json_encode($_GET));
        \Think\Log::write("POST: ".json_encode($_POST));
        print "0";
    }
    
    public function batchsend(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        $this->display();
    }
    
    public function orders(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        $this->display();
    }
    
    public function templates(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        $this->display();
    }
    
    public function tempadmin(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        
        $interfaceMap = array();
        foreach(C("SMS_INTERFACE") as $value){
            $interfaceMap[$value["key"]] = $value["name"];
        }
        $this->assign('interfaceStr', json_encode($interfaceMap));
        $this->display();
    }
    
    public function api_addsign(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $sign = $_POST["sign"];
        $signModel = M("signs");
        
        $data = array();
        $data["user_id"] = $myId;
        $data["sign"] = $sign;
        $signModel->add($data);
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function api_addtemplate(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $template = $_POST["template"];
        $templateModel = M("templates");
        
        $data = array();
        $data["user_id"] = $myId;
        $data["content"] = $template;
        $curTime = time();
        $submitTime = date('Y-m-d H:i:s', $curTime);
        $batch = date('ymdHis', $curTime);
        $data["submit_time"] = $submitTime;
        $data["name"] = $batch;
        $templateModel->add($data);
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function api_rename_template(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $name = $_POST["rename"];
        $id = $_POST["id"];
        $templateModel = M("templates");
        
        $data = array();
        $data["name"] = $name;
        $where = '';
        
        if(S($authKey.":groupId") == 1 || $myId == 5){
            $where = 'id='.$id;
        }else{
            $where = 'id='.$id.' AND user_id='.$myId;
        }
        
        $templateModel->where($where)->save($data);
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function customers(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $myId = $this->assignCommon();
        
        $userModel = M("users");
        $userInfo = $userModel->field("sms_price")->where("id=".$myId)->find();
        
        $signModel     = M("signs");
        $templateModel = M("templates");
        $signList      = $signModel->where("(user_id=".$myId." OR user_id=1 OR user_id=7) AND status=1")
                                   ->order("submit_time desc")->select();
        $templateList  = $templateModel->where("(user_id=".$myId." OR user_id=1 OR user_id=7) AND status=1")
                                   ->order("submit_time desc")->select();
        $signArr = array();
        $tempArr = array();
        $tempNameArr = array();
        foreach($signList as $value){
            $signArr[$value["id"]] = $value["sign"];
        }
        
        foreach($templateList as $value){
            $tempArr[$value["id"]] = $value["content"];
            $tempNameArr[$value["id"]] = array("name" => $value["name"], "interface" => $value["interface"]);
        }
        
        $modelTypesModel = M("data_model");
        $modelTypeList = $modelTypesModel->where("enabled=1")->order("seq")->select();
        
        $this->assign('signsStr', json_encode($signArr));
        $this->assign('templatesStr', json_encode($tempArr));
        $this->assign('templateNamesStr', json_encode($tempNameArr));
        $this->assign('modelTypeStr', json_encode($modelTypeList));
        $this->assign('mySmsPrice', $userInfo["sms_price"]);
        $this->display();
    }
    
    public function api_upload_customers(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        import('Org.Net.UploadFile');
        
        $upload = new \UploadFile();          // 实例化上传类
        $upload->maxSize  = 3145728 ;        // 设置附件上传大小
        $upload->allowExts = array('csv', 'txt', 'xlsx', 'xls');  // 设置附件上传类型
        
        $rootFolder = './uploaded_customers/';
        if(!is_dir($rootFolder)) mkdir($rootFolder);
        $savePath = $rootFolder.$myId;
        if(!is_dir($savePath)) mkdir($savePath);
        
        $upload->savePath = $savePath.'/';  // 设置附件上传目录
        //$upload->saveRule = "withTimeStamp";
        $upload->uploadReplace = true;
        
        $result = array("state"=> 200);
        if(!$upload->upload()) {  // 上传错误提示错误信息
            //$this->error($upload->getErrorMsg());
            // \Think\Log::write($upload->getErrorMsg());
            $result = array("state"=> 104, "comment" => $upload->getErrorMsg());
        }else{  // 上传成功 获取上传文件信息
            $info =  $upload->getUploadFileInfo();
            // LOG::write("info is ".json_encode($info),LOG::DEBUG);
            $fileName = $info[0]["savename"];
            $ext      = $info[0]["extension"];
            
            $fileFullPath = $savePath.'/'.$fileName;
            
            $userUploadModel = M("user_upload");
            $data = array();
            $data["user_id"]  = $myId;
            $data["uploader"] = $myId;
            $data["model"] = 1;
            $data["file"] = $fileFullPath;
            
            $userUploadModel->add($data);
            
            $countStr = trim(exec("ps -ef | grep trigerExcelParser | grep -v grep | wc -l"));
            if($countStr == 0){
                shell_exec('nohup python ./python/sms.py trigerExcelParser >/dev/null 2>&1 &');
            }
        }
        
        // \Think\Log::write(json_encode($result));
        print(json_encode($result));
    }
    
    public function api_send_sms(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $batch = $_POST["batch"];
        $content = $_POST["content"];
        $tempId = $_POST["tempId"];
        
        $batchModel = M("user_upload");
        $batchInfo = $batchModel->where("id=".$batch)->find();
        
        $userModel = M("users");
        $userInfo = $userModel->field("sms_price, sms_account")->where("id=".$myId)->find();
        
        $tempModel = M("templates");
        $tempInfo = $tempModel->field("interface")->where("id=".$tempId)->find();
        $smsConfig = C("SMS_INTERFACE");
        
        if($tempInfo == null || $tempInfo["interface"] == null 
          || !in_array($tempInfo["interface"], array_keys($smsConfig))){
            $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"短信模板未通过审批.");
            print(json_encode($result));
            exit;
        }
        $smsSendFunction = $smsConfig[$tempInfo["interface"]]["sendAction"];
        
        $result = array("state"=> 200, "title"=>"提交成功", "comment"=>"开始发送.");
        $readyToSend = false;
        if($batchInfo){
            if($batchInfo["status"] < 2){
                $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"客户列表未解析完成.");
                print(json_encode($result));
                exit;
            }
                
            if($batchInfo["model"] == 1){
                if($batchInfo["user_id"] == $myId && $batchInfo["status"] != 10 && $batchInfo["lock"] == 0){
                    $readyToSend = true;
                }else{
                    $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"客户列表正在发送中.");
                    print(json_encode($result));
                    exit;
                }
            }else{
                if($batchInfo["user_id"] == 0 && $batchInfo["status"] != 10 && $batchInfo["lock"] == 0){
                    $readyToSend = true;
                }else if($batchInfo["user_id"] == $myId && $batchInfo["status"] == 10){
                    $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"客户列表正在发送中.");
                    print(json_encode($result));
                    exit;
                }else if($batchInfo["user_id"] == $myId && $batchInfo["status"] > 2){
                    $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"客户列表已发送过.");
                    print(json_encode($result));
                    exit;
                }
            }
        }
        
        if($readyToSend){  // ready
            $modelModel = M("data_model");
            $modelInfo = $modelModel->field("data_price")->where("id=".$batchInfo["model"])->find();
            
            /*
            $chrCount = mb_strlen($content, "utf-8");
            $smsCount = ceil(($chrCount - 70)/67) + 1;
            
            $needMoney = $batchInfo["count"] * $userInfo["sms_price"] * $smsCount;
            $needMoney += $batchInfo["count"] * $modelInfo["data_price"];
            */
            
            $smsCount = $this->get_sms_count($content);
            $needMoney = $this->get_need_money($batchInfo["count"], $smsCount,
                                               $userInfo["sms_price"], $modelInfo["data_price"]);
            
            if($needMoney > $userInfo["sms_account"]){
                $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"余额不足.");
                print(json_encode($result));
                return;
            }
            
            $data = array();
            $data["status"] = 10;  // 提交中
            $data["sent_times"] = $batchInfo["sent_times"] + 1;
            if($batchInfo["model"] > 1 && $batchInfo["user_id"] == 0){
                $data["user_id"] = $myId;
            }
            $batchModel->where("id=".$batch)->save($data);
            
            $batchStr = $batchInfo["batch"];
            $uploader = $batchInfo["uploader"];
            $detailModel = M("uu".$uploader."_".$batchStr);
            $detailList = $detailModel->field("phone")->select();
            
            $phones = array(); // 二维数组
            $phones[] = array();
            $batchMaxCount = 1000;
            foreach($detailList as $key => $value){
                $curBatchIndex = count($phones) - 1;
                if(count($phones[$curBatchIndex]) >= $batchMaxCount){
                    $phones[] = array();
                    $curBatchIndex += 1;
                }
                $phones[$curBatchIndex][] = $value["phone"];
            }
            
            $leftMoney =  $userInfo["sms_account"];
            foreach($phones as $phonesBatch){
                $ret = array();
                $ret = $this->$smsSendFunction($batch, $batchStr, $content, $phonesBatch, 
                                               $userInfo["sms_price"], $modelInfo["data_price"]);
                if($ret === false) {
                    $result = array("state"=> 104, "title"=>"发送失败", "comment"=>"请检查发送记录.");
                    break;
                }else{
                    $data = array();
                    $batchNeedMoney = $this->get_need_money(count($phonesBatch), $smsCount,
                                                            $userInfo["sms_price"], $modelInfo["data_price"]);
                    $leftMoney = $leftMoney - $batchNeedMoney;
                    $data["sms_account"] = $leftMoney;
                    $userModel->where("id=".$myId)->save($data);
                    
                    $recordModel = M("charge_record");
                    $recordData = array();
                    $recordData["operator"] = $myId;
                    $recordData["for_user"] = $myId;
                    $recordData["add_money"] = 0 - $batchNeedMoney;
                    $recordData["final_money"] = $data["sms_account"];
                    $recordData["reason"] = 1;  // send cost
                    $recordData["task"] = $ret["task"];
                    
                    $recordModel->add($recordData);
                }
            }
                                           
            // need judgement to choose interface here
            //$ret = $this->channelSendVia178($batch, $batchStr, $content, $phones, 
            //                               $userInfo["sms_price"], $modelInfo["data_price"]);
            //$ret = $this->channelSendVia82($batch, $batchStr, $content, $phones, 
            //                               $userInfo["sms_price"], $modelInfo["data_price"]);
        }else{
            $result = array("state"=> 104, "title"=>"提交失败", "comment"=>"客户列表已被占用.");
        }
        print(json_encode($result));
    }
    
    private function get_sms_count($content){
        $chrCount = mb_strlen($content, "utf-8");
        $smsCount = ceil(($chrCount - 70)/67) + 1;
        return $smsCount;
    }
    
    private function get_need_money($batchCount, $smsCount, $smsPrice, $dataPrice){
        $needMoney = $batchCount * $smsPrice * $smsCount;
        $needMoney += $batchCount * $dataPrice;
        return $needMoney;
    }
    
    public function api_get_history(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $batchId = $_POST["selectedId"];
        
        $recordModel = M("send_record");
        $list = $recordModel->where('batch_id='.$batchId)->order('sent_time DESC')->select();
        
        $result = array("state"=> 200, "title"=>"提交成功", "comment"=>$list);
        print(json_encode($result));
    }
    
    private function channelSendVia178($batch, $batchStr, $content, $phones, $smsPrice, $dataPrice){
        $interfaceId = "sms178";
        $phoneStr = implode(",", $phones);
        
        $sendUrl = "http://139.224.60.78:8888/sms.aspx";
        $data = array();
        $data["userid"] = "6436";
        $data["account"] = "1065731968";
        $data["password"] = "gdjm888888";
        $data["mobile"] = $phoneStr;
        $data["content"] = $content;
        $data["sendTime"] = "";
        $data["action"] = "send";
        $data["extno"] = "";
        
        $checkResult = $this->channelCheckContent178($data);
        if($checkResult !== true){
            $result = array("state"=> 104, "title"=>"提交失败", "comment"=> $checkResult);
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 2;
            $batchModel->where("id=".$batch)->save($data);
            print(json_encode($result));
            exit;
        }
        
        \Think\Log::write("channelSendVia178: ".json_encode($data));
        $ret = http_post($sendUrl, $data);
        
        $xml = simplexml_load_string($ret);
        $status = (string)$xml->returnstatus;  //这里返回的依然是个SimpleXMLElement对象
        
        $result = true;
        if($status == "Success"){
            $remainpoint = (string)$xml->remainpoint;
            $successCounts = (string)$xml->successCounts;
            $taskID = (string)$xml->taskID;
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 20;
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = $taskID;
            $data["all_count"] = count($phones);
            //$data["sent_count"] = $successCounts;
            $data["sent_count"] = 0;
            $data["status"] = 1;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = $smsPrice;
            $data["data_price"] = $dataPrice;
            $data["phone_str"] = json_encode($phones);
            $recordModel->add($data);
            
            $this->startPython($interfaceId);
            
            $result = $data;
        }else{
            $message = (string)$xml->message;
            $result = false;
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 14;
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = 0;
            $data["all_count"] = count($phones);
            $data["sent_count"] = 0;
            $data["status"] = 0;
            $data["message"] = $message;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = 0;
            $data["data_price"] = 0;
            $recordModel->add($data);
        }
        
        return $result;
    }
    
    private function channelSendVia82($batch, $batchStr, $content, $phones, $smsPrice, $dataPrice){
        $interfaceId = "sms82";
        $phoneStr = implode(",", $phones);
        
        $sendUrl = "http://112.90.145.10:8718/smsgwhttp/sms/submit";
        $data = array();
        $data["spid"] = "729631";
        $data["ac"] = "1069069496310";
        $data["password"] = "1234QWER";
        $data["mobiles"] = $phoneStr;
        $data["content"] = $content;
        
        $ret = http_post($sendUrl, $data);
        
        $xml = simplexml_load_string($ret);
        $status = (string)$xml->result;  //这里返回的依然是个SimpleXMLElement对象
        
        $result = true;
        if($status == "0"){
            $taskID = (string)$xml->taskid;
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 20;  //提交成功
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = $taskID;
            $data["all_count"] = count($phones);
            $data["status"] = 1;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = $smsPrice;
            $data["data_price"] = $dataPrice;
            $data["phone_str"] = json_encode($phones);
            $recordModel->add($data);
            
            $this->startPython($interfaceId);
            
            $result = $data;
        }else{
            $message = (string)$xml->desc;
            $result = false;
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 14;  //提交失败
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = 0;
            $data["all_count"] = count($phones);
            $data["sent_count"] = 0;
            $data["status"] = 0;
            $data["message"] = $message;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = 0;
            $data["data_price"] = 0;
            $recordModel->add($data);
        }
        
        return $result;
    }
    
    private function channelSendVia52($batch, $batchStr, $content, $phones, $smsPrice, $dataPrice){
        $interfaceId = "sms52";
        $phoneStr = implode(",", $phones);
        
        $sendUrl = "http://ms.imkerry.com/smc/sms/send/";
        $data = array();
        $data["user"] = "nm1013";
        $data["pwd"] = "nm1013";
        $data["dest"] = $phoneStr;
        $data["msg"] = $content;
        //$data["ext"] = "101";
        //$data["cc"] = "102";
        //$data["msgid"] = "103";
        
        $ret = http_post($sendUrl, $data);
        
        \Think\Log::write($ret);
        
        $retParts = explode(":", $ret);
        $status = $retParts[0];
        
        $result = true;
        if($status == "0"){
            $taskID = $retParts[1];
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 20;  //提交成功
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = $taskID;
            $data["all_count"] = count($phones);
            $data["status"] = 1;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = $smsPrice;
            $data["data_price"] = $dataPrice;
            $data["phone_str"] = json_encode($phones);
            $recordModel->add($data);
            
            $result = $data;
        }else{
            $message = $status;
            $result = false;
            
            $batchModel = M("user_upload");
            $data = array();
            $data["status"] = 14;  //提交失败
            $batchModel->where("id=".$batch)->save($data);
            
            $recordModel = M("send_record");
            $data = array();
            $data["batch_id"] = $batch;
            $data["task"] = 0;
            $data["all_count"] = count($phones);
            $data["sent_count"] = 0;
            $data["status"] = 0;
            $data["message"] = $message;
            $data["content"] = $content;
            $data["interface"] = $interfaceId;
            $data["sms_price"] = 0;
            $data["data_price"] = 0;
            $recordModel->add($data);
        }
        
        return $result;
    }
    
    private function startPython($interfaceId){
        $countStr = trim(exec('ps -ef | grep "trigerGetSmsStatus '.$interfaceId.'" | grep -v grep | wc -l'));
        if($countStr == 0){
            //$cmd = 'nohup python ./python/sms.py trigerGetSmsStatus '.$interfaceId.' >/dev/null 2>&1 &';
            $cmd = 'nohup python ./python/sms.py trigerGetSmsStatus '.$interfaceId.' >> ./python/st'.$interfaceId.'.log &';
            shell_exec($cmd);
        }
        
        $countStr = trim(exec('ps -ef | grep "getReply '.$interfaceId.'" | grep -v grep | wc -l'));
        if($countStr == 0){
            shell_exec('nohup python ./python/sms.py getReply '.$interfaceId.' >/dev/null 2>&1 &');
        }
    }
    
    private function channelCheckContent178($data){
        $sendUrl = "http://139.224.60.78:8888/sms.aspx";
        unset($data["mobile"]);
        $data["action"] = "checkkeyword";
        
        $ret = http_post($sendUrl, $data);
        $xml = simplexml_load_string($ret);
        $returnstatus = (string)$xml->returnstatus;
        $message = (string)$xml->message;
        
        if($returnstatus != "Success"){
            return $message;
        }
        return true;
    }
    
    public function api_get_signlist(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $listModel = M("signs");
        $lists = $listModel->where("user_id=".$myId." OR ((user_id=1 OR user_id=7) AND status=1)")->order("submit_time desc")->select();
        
        foreach($lists as $key => $tuple){
            //$lists[$key]["sign"] = "【".$tuple["sign"]."】";
            switch($tuple["status"]){
                case 0:
                    $lists[$key]["status"] = "审核中";
                break;
                case 1:
                    $lists[$key]["status"] = "审核通过";
                break;
                case -1:
                    $lists[$key]["status"] = "驳回";
                break;
            }
        }
        
        $result = array();
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_get_signlist_all(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $listModel = M("signs");
        $lists = $listModel->where(1)->order("submit_time desc")->select();
        
        foreach($lists as $key => $tuple){
            //$lists[$key]["sign"] = "【".$tuple["sign"]."】";
            switch($tuple["status"]){
                case 0:
                    $lists[$key]["status"] = "审核中";
                break;
                case 1:
                    $lists[$key]["status"] = "审核通过";
                break;
                case -1:
                    $lists[$key]["status"] = "驳回";
                break;
            }
        }
        
        $result = array();
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_get_replies(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $listModel = M("sms_replies");
        $lists = $listModel->where("user_id=".$myId)->order("get_time desc")->select();
        
        $result = array();
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_edit_batchname(){
        $oper = $_POST["oper"];
        switch($oper){
            case "edit":
                $id = $_POST["id"];
                $name = $_POST["name"];
                $data = array();
                $data["name"] = $name;
                $batchModel = M("user_upload");
                $batchModel->where("id=".$id)->save($data);
            break;
        }
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function api_edit_signadmin(){
        $oper = $_POST["oper"];
        switch($oper){
            case "edit":
                $id = $_POST["id"];
                $sign = $_POST["sign"];
                $status = $_POST["status"];
                $signModel = M("signs");
                $data = array();
                $data["sign"] = $sign;
                $data["status"] = $status;
                $data["interface"] = $_POST["interface"];
                $signModel->where("id=".$id)->save($data);
            break;
        }
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function api_edit_tempadmin(){
        $oper = $_POST["oper"];
        switch($oper){
            case "edit":
                $id = $_POST["id"];
                $content = $_POST["content"];
                $status = $_POST["status"];
                $signModel = M("templates");
                $data = array();
                $data["content"] = $content;
                $data["status"] = $status;
                $data["comment"] = $_POST["comment"];
                $data["interface"] = $_POST["interface"];
                $signModel->where("id=".$id)->save($data);
            break;
        }
        
        $result = array("state"=> 200);
        print(json_encode($result));
    }
    
    public function api_get_templatelist(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $listModel = M("templates");
        $lists = $listModel->where("user_id=".$myId." OR ((user_id=1 OR user_id=7) AND status=1)")->order("submit_time desc")->select();
        
        foreach($lists as $key => $tuple){
            switch($tuple["status"]){
                case 0:
                    $lists[$key]["status"] = "审核中";
                break;
                case 1:
                    $lists[$key]["status"] = "审核通过";
                break;
                case -1:
                    $lists[$key]["status"] = "驳回";
                break;
            }
        }
        
        $result = array();
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_get_templatelist_all(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $listModel = M("templates");
        $lists = $listModel->where(1)->order("submit_time desc")->select();
        
        foreach($lists as $key => $tuple){
            switch($tuple["status"]){
                case 0:
                    $lists[$key]["status"] = "审核中";
                break;
                case 1:
                    $lists[$key]["status"] = "审核通过";
                break;
                case -1:
                    $lists[$key]["status"] = "驳回";
                break;
            }
        }
        
        $result = array();
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_get_custlists(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $modelType = $_GET["modeltype"];
        
        $listModel = M("user_upload");
        $lists = array();
        
        if($modelType == 0){
            // $where = "(model=1 AND user_id=".$myId.") OR model!=1";
            $where = 'user_id=0 OR user_id='.$myId;
            if(S($authKey.":groupId") == 1)
                $where = "(model=1) OR model!=1";
            $lists = $listModel->where($where)->order("uploadtime desc")->select();
        }else if($modelType == 1){
            $where = "model=1 AND user_id=".$myId;
            if(S($authKey.":groupId") == 1)
                $where = "model=1";
            $lists = $listModel->where($where)->order("uploadtime desc")->select();
        }else{
            $where = 'model='.$modelType.' AND (user_id=0 OR user_id='.$myId.')';
            if(S($authKey.":groupId") == 1)
                $where = 'model='.$modelType;
            $lists = $listModel->where($where)->order("uploadtime desc")->select();
        }
        
        foreach($lists as $key => $tuple){
            $lists[$key]["file"] = preg_replace("/.*\//is", "", $tuple["file"]);
            if($tuple["model"] > 1 && $tuple["user_id"] > 0 && $tuple["user_id"] != $myId){
                $lists[$key]["lock"] = 1;
                $lists[$key]["user_id"] = -1;
            }else if($tuple["model"] > 1 && $tuple["status"] > 2){
                $lists[$key]["lock"] = 1;
            }
        }
        
        $result = array();
        /*
        $result["page"] = $page;
        $result["total"] = ceil($count/$nums);
        $result["records"] = $count;
        */
        $result["rows"] = $lists;
        
        print(json_encode($result));
    }
    
    public function api_get_custdetail(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $batchModel = M("user_upload");
        $batchInfo = $batchModel->where("id=".$_GET["id"])->find();
        $modelType = $batchInfo["model"];
        
        $modelModel = M("data_model");
        $modelInfo = $modelModel->field("name")->where("id=".$modelType)->find();
        
        if($batchInfo){
            if(S($authKey.":groupId") == 1 || $modelType > 1 || ($modelType == 1 && $batchInfo["user_id"] == $myId)){
                $batch    = $batchInfo["batch"];
                $uploader = $batchInfo["uploader"];
                $modelTable = "uu".$uploader."_".$batch;
                $detailModel = M($modelTable);
                
                $detailList = $detailModel->select();
                $isFreeNumber = false;
                if($modelType == 9 || $modelType == 10 || $modelType == 11){
                    $isFreeNumber = true;
                }
                
                \Think\Log::write(count($detailList));
                
                if($modelType > 1){
                    foreach($detailList as $key =>$value){
                        $detailList[$key]["cust_name"] = "已脱敏";
                        if($isFreeNumber){
                            if($batchInfo["user_id"] != $myId && $batchInfo["status"] > 2 
                              && S($authKey.":groupId") > 1){
                                $detailList[$key]["last_receive_time"] = "";
                                $detailList[$key]["sent_comment"] = "已占用";
                                $detailList[$key]["comment"] = "来源于".$modelInfo["name"]."数据模型";
                                $detailList[$key]["status"] = "2";
                            }else if($detailList[$key]["comment"] == "")
                                $detailList[$key]["comment"] = "来源于".$modelInfo["name"]."数据模型";
                        }else{
                            if(S($authKey.":groupId") > 1)
                                $detailList[$key]["phone"] = preg_replace("/(\d{2})\d{5}(\d{4}).*/iu", "$1*****$2", $value["phone"]);
                            if($value["comment"] == ""){
                                $detailList[$key]["comment"] = "来源于".$modelInfo["name"]."数据模型";
                            }
                            if($batchInfo["user_id"] != $myId && $batchInfo["status"] > 2 && S($authKey.":groupId") > 1){
                                $detailList[$key]["last_receive_time"] = "";
                                $detailList[$key]["sent_comment"] = "已占用";
                                $detailList[$key]["status"] = "2";
                            }
                        }
                    }
                }
                
                $result = array();
                $result["rows"] = $detailList;
                $result["state"] = 200;
                
                print(json_encode($result));
            }else{
                $result = array("state"=> 104);
                print(json_encode($result));
            }
        }else print "no batchInfo";
        
    }
    
    private function needLogin(){
        header('Location: '.C("WEB_ROOT")."login");
        exit;
    }
    
    private function assignCommon(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $this->assign('userName', S($authKey.":showName"));
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('sitename', C("SITE_NAME"));
        $this->assign('myId', $myId);
        
        $isMobile = 0;
        if(is_mobile()) $isMobile = 1;
        $this->assign('isMobile', $isMobile);
        return $myId;
    }
}
?>