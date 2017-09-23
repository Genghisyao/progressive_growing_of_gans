<?php
namespace Home\Controller;
use Think\Controller;

class BrokerController extends Controller {
    public function index(){
      print "here".$_POST['email']." ".$_POST['password'];
    }
    
    function _empty(){ 
        header("HTTP/1.0 404 Not Found");//使HTTP返回404状态码 
        $this->assign('error_reason',"(操作方法不存在)");
        $this->display("Public:error-404"); 
    }
    
    public function group(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $this->display();
    }
    
    public function api_addbroker(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        
        if($_POST["name"] != ""){
            $data["name"] = $_POST["name"];
            $data["address"] = $_POST["address"];
            $data["hotline"] = $_POST["hotline"];
            $data["top"] = $_POST["isTop"];
            $data["owner"] = S($authKey.":userId");
            
            $brokerModel = M("brokergroup");
            $hasLine = $brokerModel->where('name="'.$data["name"].'"')->limit(1)->select();
            if(count($hasLine) == 0){
                $brokerModel->add($data);
                $result = array ("state"=>200,"title"=>"操作成功","comment"=>"添加机构 [".$data["name"]."] 成功");
                print json_encode($result);
            }else{
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构 [".$data["name"]."] 已存在");
                print json_encode($result);
            }
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构名称不能为空");
            print(json_encode($result));
        }
    }
    
    public function api_getbroker_users(){
        auth(__CLASS__,__FUNCTION__);
        $targetBrokerId = I('path.2');
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $userModel = M("users");
        $myInfo = $userModel->where("id=".$myId)->limit(1)->select();
        $myAsgnBkId = $myInfo[0]["asgn_broker"];
        if($myAsgnBkId == "") $myAsgnBkId = 0;
        
        $allAvailableUsers = $userModel->field("id,nickname")
        ->where("id!=".$myId." AND orgn_broker=".$myAsgnBkId." AND (asgn_broker=-1 OR asgn_broker=".$targetBrokerId.")")
        ->select();
        $allSelectedUsers = $userModel->field("id,nickname")
        ->where("id!=".$myId." AND orgn_broker=".$myAsgnBkId." AND asgn_broker=".$targetBrokerId)
        ->select();
        
        $result = array ("state"=>200,"availableUser" => $allAvailableUsers,"selectedUser" => $allSelectedUsers);
        print json_encode($result);
    }
    
    public function api_getbrokergroup_list(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        
        $list = $this->get_my_brokergroup_list();
        $inactiveList = $this->getbrokergroup_list("parent_id=-1");
        
        $result = array ("state"=>200,"topParent"=>$list[1],"topId"=>S($authKey.":userBrokerId"),
        "brokerGroupList"=> $list[0],"inactiveBroker" => $inactiveList);
        print(json_encode($result));
    }
    
    private function get_my_brokergroup_list(){
        $authKey = $_COOKIE['authKey'];
        $brokerModel = M("brokergroup");
        $brokerTable = C('DB_PREFIX').'brokergroup';
        $userTable = C('DB_PREFIX').'users';
        $userBrokerId = S($authKey.":userBrokerId");
        
        $isOwnAll = false;
        $condition = "b.id=".$userBrokerId;
        
        if($userBrokerId == 0){
            $isOwnAll = true;
            $condition = "parent_id>-1";
        }
        
        $brokerList = $brokerModel->table($brokerTable." b")
        ->join('LEFT JOIN '.$userTable.' u on b.owner=u.id')
        ->field('b.*, u.login_name, u.nickname')
        ->order("b.sequence")
        ->where($condition." AND b.deleted=0")
        ->select();
        
        $resultArr = array();
        $topParent = 0;
        if(count($brokerList) > 0 && !$isOwnAll){
            $topParent = $brokerList[0]["parent_id"];
            for($i=0;$i<count($brokerList);$i++){
                $initArr = array();
                $subResultArr = $this->getChildBrokerList($brokerList[$i]["id"], $initArr,$isOwnAll);
                $resultArr = array_merge($resultArr, $subResultArr);
            }
        }
        
        if(count($resultArr) > 0) return array(array_merge($brokerList, $resultArr),$topParent);
        if(count($brokerList) < 1) $brokerList = array();
        return array($brokerList,$topParent);
    }
    
    private function getChildBrokerList($bId, $resultArr, $isOwned){
        $authKey = $_COOKIE['authKey'];
        $brokerModel = M("brokergroup");
        $brokerTable = C('DB_PREFIX').'brokergroup';
        $userTable = C('DB_PREFIX').'users';
        $boxModel = M("user_box");
        $myId = S($authKey.":userId");
        
        $condition = "b.parent_id=".$bId;
        if(!$isOwned) $condition = "b.owner=".$myId." AND b.parent_id=".$bId;
        
        $brokerList = $brokerModel->table($brokerTable." b")
        ->join($userTable.' u on u.id=b.owner')
        //->join($boxTable.' box on box.brokerId=b.id')
        ->field('b.*, u.login_name, u.nickname')
        ->order("b.sequence")
        ->where($condition." AND b.deleted=0")
        ->select();
        
        foreach($brokerList as $key=>$broker){
            $activeBoxCount = $boxModel->where("user_id<>0 AND brokerId=".$broker["id"])->count();
            $brokerList[$key]["activeBoxCount"] = $activeBoxCount;
            $inActiveBoxCount = $boxModel->where("user_id=0 AND brokerId=".$broker["id"])->count();
            $brokerList[$key]["inActiveBoxCount"] = $inActiveBoxCount;
        }
        
        $subResultArr = array();
        
        if(count($brokerList) > 0){
            $subResultArr = array_merge($resultArr, $brokerList);
            foreach($brokerList as $key=>$broker){
                if($broker["owner"] == $myId) $isOwned = true;
                $subResultArr = $this->getChildBrokerList($broker["id"], $subResultArr, $isOwned);
            }
        }else $subResultArr = $resultArr;
        
        return $subResultArr;
    }
    
    private function getbrokergroup_list($condition){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $brokerModel = M("brokergroup");
        $brokerTable = C('DB_PREFIX').'brokergroup';
        $userTable = C('DB_PREFIX').'users';
        
        $brokerList = $brokerModel->table($brokerTable." b")
        ->join($userTable.' u on b.owner=u.id')
        ->field('b.*, u.login_name, u.nickname')
        ->order("b.sequence")
        ->where($condition." AND b.deleted=0 AND b.owner=".$myId)
        ->select();
        
        if(count($brokerList) < 1) $brokerList = array();
        return $brokerList;
    }
    
    public function api_modify_broker_info(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $id = $_POST["id"];
        $name = $_POST["name"];
        $address = $_POST["address"];
        $hotline = $_POST["hotline"];
        $top = $_POST["isTop"];
        $addList = $_POST["addUser"];
        $delList = $_POST["delUser"];
        
        if($id == null || $id == "") return;
        
        if($name == null | $name == ""){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构名称不能为空.");
            print(json_encode($result));
            exit;
        }
        
        $data["name"] = $name;
        $data["address"] = $address;
        $data["hotline"] = $hotline;
        $data["top"] = $top;
        
        $brokerModel = M("brokergroup");
        $hasLine = $brokerModel->where('name="'.$data["name"].'"')->limit(1)->select();
        if(count($hasLine) == 0 || $hasLine[0]["id"] == $id){
            $brokerModel->where("id=".$id)->save($data);
            
            $userModel = M("users");
            $myId = S($authKey.":userId");
            $myInfo = $userModel->where("id=".$myId)->limit(1)->select();
            $myAsgnBkId = $myInfo[0]["asgn_broker"];
            
            $addArr = explode(",",$addList);
            foreach($addArr as $adduser){
                if($adduser == "") continue;
                $hasAddedUser = $userModel->where("id=".$adduser." AND orgn_broker=".$myAsgnBkId)->limit(1)->select();
                if(count($hasAddedUser) > 0) {
                  $addUserData["asgn_broker"] = $id;
                  $userModel->where("id=".$adduser)->save($addUserData);
                }
            }
            $delArr = explode(",",$delList);
            foreach($delArr as $deluser){
                if($deluser == "") continue;
                $hasDelUser = $userModel->where("id=".$deluser." AND orgn_broker=".$myAsgnBkId)->limit(1)->select();
                if(count($hasDelUser) > 0) {
                  $delUserData["asgn_broker"] = -1;
                  $userModel->where("id=".$deluser)->save($delUserData);
                }
            }
            
            $result = array ("state"=>200,"title"=>"修改成功","comment"=>"机构资料已保存.");
            print(json_encode($result));
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构 [".$data["name"]."] 已存在");
            print json_encode($result);
        }
    }
    
    public function api_change_broker_struct(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        
        $jsonStr = $_POST["structJsonStr"];
        $jsonArray = json_decode($jsonStr, true);
        //$userBrokerId = S($authKey.":userBrokerId");
        
        $userModel = M("users");
        $myId = S($authKey.":userId");
        $myInfo = $userModel->where("id=".$myId)->find();
        $userBrokerId = $myInfo["asgn_broker"];
        if($userBrokerId == null) exit;
        
        $brokerModel = M("brokergroup");
        $this->setParent($brokerModel, $userBrokerId, $jsonArray);
        
        $result = array ("state"=>200);
        print(json_encode($result));
    }
    
    public function api_add_boxes(){
        auth(__CLASS__,__FUNCTION__);
        $startNumber = $_POST["start"];
        $endNumber = $_POST["end"];
        $brokerId = $_POST["broker"];
        
        if($brokerId == null || $brokerId == ""){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构数据丢失");
            print json_encode($result);
            exit;
        }
        
        if(!$this->isPhone($startNumber) || !$this->isPhone($endNumber)){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"手机号码格式不对");
            print json_encode($result);
            exit;
        }
        
        $tempNum = $startNumber;
        $count = 0;
        $maxCount = 5000;
        $found = false;
        for($i=0;$i<=5000 && !$found;$i++){
            if($tempNum == $endNumber) $found = true;
            $count ++;
            $tempNum ++;
        }
        
        if($count > $maxCount){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"号码段的号码数大于".$maxCount);
            print json_encode($result);
            exit;
        }
        
        $brokerModel = M("brokergroup");
        $parentBrokerId = 0;
        $hasBroker = $brokerModel->field("parent_id")->where("id=".$brokerId)->limit(1)->select();
        if(count($hasBroker) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"该机构不存在");
            print json_encode($result);
            exit;
        }else $parentBrokerId = $hasBroker[0]["parent_id"];
        
        $boxModel = M("user_box");
        $tempNum = $startNumber;
        $count = 0;
        $found = false;
        while(!$found){
            $hasBox = $boxModel->where('box_name="'.$tempNum.'"')->limit(1)->select();
            if($hasBox < 1){
                $data["box_name"] = $tempNum;
                $data["brokerId"] = $brokerId;
                $boxModel->add($data);
                $count ++;
            }
            if($tempNum == $endNumber) $found = true;
            $tempNum ++;
        }
        $getResult = $this->getBrokerEmptyBox($brokerId);
        
        $result = array ("state" => 200,"title" => "操作成功","count" => $count, 
        "cStartNum" => $getResult[0], "cCount" => $getResult[1],
        "pStartNum" => $getResult[2], "pCount" => $getResult[3]);
        print json_encode($result);
    }
    
    public function api_distribute_boxes(){
        auth(__CLASS__,__FUNCTION__);
        $startNumber = $_POST["start"];
        $count = $_POST["count"];
        $isAll = $_POST["isAll"];
        $brokerId = $_POST["broker"];
        
        if($brokerId == null || $brokerId == ""){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构数据丢失");
            print json_encode($result);
            exit;
        }
        
        if(!$this->isPhone($startNumber)){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"手机号码格式不对");
            print json_encode($result);
            exit;
        }
        
        $brokerModel = M("brokergroup");
        $parentBrokerId = 0;
        $hasBroker = $brokerModel->field("parent_id")->where("id=".$brokerId)->limit(1)->select();
        if(count($hasBroker) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"该机构不存在");
            print json_encode($result);
            exit;
        }else $parentBrokerId = $hasBroker[0]["parent_id"];
        
        $boxModel = M("user_box");
        $tempNum = $startNumber;
        $currentCount = 0;
        $maxCount = 5000;
        $found = true;
        while($found && ($isAll == 1 || $currentCount < $count) && $currentCount < $maxCount){
            $hasBox = $boxModel->where('box_name="'.$tempNum.'" AND user_id=0')->limit(1)->select();
            if($hasBox > 0 && $hasBox[0]["brokerId"] == $parentBrokerId){
                $data["brokerId"] = $brokerId;
                $boxModel->where("id=".$hasBox[0]["id"])->save($data);
                $currentCount ++;
            } else $found = false;
            $tempNum ++;
        }
        $getResult = $this->getBrokerEmptyBox($brokerId);
        
        $result = array ("state" => 200,"title" => "操作成功","count" => $currentCount, 
        "cStartNum" => $getResult[0], "cCount" => $getResult[1],
        "pStartNum" => $getResult[2], "pCount" => $getResult[3]);
        print json_encode($result);
    }
    
    public function api_return_boxes(){
        auth(__CLASS__,__FUNCTION__);
        $startNumber = $_POST["start"];
        $count = $_POST["count"];
        $isAll = $_POST["isAll"];
        $brokerId = $_POST["broker"];
        
        if($brokerId == null || $brokerId == ""){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"机构数据丢失");
            print json_encode($result);
            exit;
        }
        
        if(!$this->isPhone($startNumber)){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"手机号码格式不对");
            print json_encode($result);
            exit;
        }
        
        $brokerModel = M("brokergroup");
        $parentBrokerId = 0;
        $hasBroker = $brokerModel->field("parent_id")->where("id=".$brokerId)->limit(1)->select();
        if(count($hasBroker) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"该机构不存在");
            print json_encode($result);
            exit;
        }else $parentBrokerId = $hasBroker[0]["parent_id"];
        
        $boxModel = M("user_box");
        $tempNum = $startNumber;
        $currentCount = 0;
        $maxCount = 5000;
        $found = true;
        while($found && ($isAll == 1 || $currentCount < $count) && $currentCount < $maxCount){
            $hasBox = $boxModel->where('box_name="'.$tempNum.'" AND user_id=0')->limit(1)->select();
            if($hasBox > 0 && $hasBox[0]["brokerId"] == $brokerId){
                $data["brokerId"] = $parentBrokerId;
                $boxModel->where("id=".$hasBox[0]["id"])->save($data);
                $currentCount ++;
            } else $found = false;
            $tempNum ++;
        }
        $getResult = $this->getBrokerEmptyBox($brokerId);
        
        $result = array ("state" => 200,"title" => "操作成功","count" => $currentCount, 
        "cStartNum" => $getResult[0], "cCount" => $getResult[1],
        "pStartNum" => $getResult[2], "pCount" => $getResult[3]);
        print json_encode($result);
    }
    
    public function api_get_empty_box(){
        auth(__CLASS__,__FUNCTION__);
        $targetBrokerId = $_GET["_URL_"][2];
        
        $getResult = $this->getBrokerEmptyBox($targetBrokerId);
        
        $result = array ("state" => 200,"title" => "操作成功", 
        "cStartNum" => $getResult[0], "cCount" => $getResult[1],
        "pStartNum" => $getResult[2], "pCount" => $getResult[3]);
        print json_encode($result);
    }
    
    private function getBrokerEmptyBox($brokerId){
        $brokerModel = M("brokergroup");
        $parentBrokerId = 0;
        $hasBroker = $brokerModel->field("parent_id")->where("id=".$brokerId)->limit(1)->select();
        if(count($hasBroker) < 1) exit;
        else $parentBrokerId = $hasBroker[0]["parent_id"];
        
        $boxModel = M("user_box");
        $currentEmpty = $boxModel->field("box_name")->where('brokerId='.$brokerId.' AND user_id=0')->order("box_name")->select();
        $currentEmptyStart = array();
        $currentEmptyCount = array();
        
        $tempNum = "blank";
        $tempCount = 0;
        for($i=0;$i < count($currentEmpty); $i++){
            if($currentEmpty[$i]["box_name"] != $tempNum){
                if(count($currentEmptyStart) > 0){
                    $currentEmptyCount[count($currentEmptyStart) -1] = $tempCount;
                }
                $tempNum = $currentEmpty[$i]["box_name"];
                $currentEmptyStart[] = $tempNum;
                $tempCount = 0;
            }
            
            $tempCount++;
            $tempNum ++;
        }
        if(count($currentEmptyStart) > 0) $currentEmptyCount[count($currentEmptyStart) -1] = $tempCount;
        
        $parentEmpty = $boxModel->field("box_name")->where('brokerId='.$parentBrokerId.' AND user_id=0')->order("box_name")->select();
        $parentEmptyStart = array();
        $parentEmptyCount = array();
        
        $tempNum = "blank";
        $tempCount = 0;
        for($i=0;$i < count($parentEmpty); $i++){
            if($parentEmpty[$i]["box_name"] != $tempNum){
                if(count($parentEmptyStart) > 0){
                    $parentEmptyCount[count($parentEmptyStart) -1] = $tempCount;
                }
                $tempNum = $parentEmpty[$i]["box_name"];
                $parentEmptyStart[] = $tempNum;
                $tempCount = 0;
            }
            
            $tempCount++;
            $tempNum ++;
        }
        if(count($parentEmptyStart) > 0) $parentEmptyCount[count($parentEmptyStart) -1] = $tempCount;
        
        return array($currentEmptyStart,$currentEmptyCount,$parentEmptyStart,$parentEmptyCount);
    }
    
    public function api_delete_broker(){
        auth(__CLASS__,__FUNCTION__);
        $brokerId = I('path.2');
        if($brokerId == "") return;
        
        $brokerModel = M("brokergroup");
        $hasChild = $brokerModel->where("parent_id=".$brokerId)->limit(1)->select();
        if(count($hasChild) > 0){
          $result = array ("state"=>104,"title"=>"删除失败","comment"=>"指定机构有下属机构, 不可删除.");
          print(json_encode($result));
        }else{
            $userModel = M("users");
            $hasUser = $userModel->where("asgn_broker=".$brokerId)->find();
            if($hasUser){
              $result = array ("state"=>104,"title"=>"删除失败","comment"=>"指定机构有下属成员, 不可删除.");
              print(json_encode($result));
            }else{
              $data["deleted"]  = 1;
              $brokerModel->where("id=".$brokerId)->save($data);
              $result = array ("state"=>200,"title"=>"删除成功","comment"=>"指定机构已删除");
              print(json_encode($result));
            }
        }
    }
    
    private function assignCommon(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $this->assign('userName', S($authKey.":showName"));
        $this->assign('webroot', C("WEB_ROOT"));
        $completion = S("user:".$myId.":infoCompletion");
        if($completion == null || $completion == ""){
            $UserModel = new UserAction();
            $UserModel->checkUserInfoCompletion();
            $completion = S("user:".$myId.":infoCompletion");
        }
        $this->assign('infoCompleteJson', $completion);
        
        // inFormArr is generated by User Action
        $inFormArr = S("user:".$myId.":inform");
        if($inFormArr == null) $inFormArr = "[]";
        $this->assign('informJson', $inFormArr);
    }
    
    private function setParent($m, $p, $jsonArr){
        for($i=0;$i < count($jsonArr);$i++){
            $data["parent_id"] = $p;
            $m->where("id=".$jsonArr[$i]["id"])->save($data);
            if(isset($jsonArr[$i]["children"])){
                $this->setParent($m, $jsonArr[$i]["id"],$jsonArr[$i]["children"]);
            }
        }
    }
    
    private function checkEmailFormat($email){
        if (ereg("^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-])+",$email)) {
            return true;
        }
        return false;
    }
    
    private function isPhone($phone){
        if(preg_match("/1[3458]{1}\d{9}$/", $phone)) return true;
        else return false;
    }
}