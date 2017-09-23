<?php
namespace Home\Controller;
use Think\Controller;

class UserController extends Controller {
    public function index(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
        
        $groupModel = M("usergroup");
        $groupTable = C('DB_PREFIX').'usergroup';
        $groupTypeTable = C('DB_PREFIX')."usergrouptype";
        $userTable = C('DB_PREFIX').'users';
        $modelResult = $groupModel->table($groupTable." g")
        ->join('LEFT JOIN '.$groupTypeTable.' t on t.id=g.group_type')
        ->join('LEFT JOIN '.$userTable.' u on u.group_id=g.id')
        ->field("t.name as type_name, t.id as type_id, g.id as id, g.name as name, count(u.id) as count")
        ->group('g.id')->where('g.level > '.S($authKey.":level"))
        ->select();
        
        $groups = array();
        foreach($modelResult as $value){
                $groups[$value["type_name"]][]= array($value["id"], $value["name"], $value["count"], $value["type_id"]);
        }
        
        $this->assign('groups', $groups);
        
        $this->display();
    }
    
    function _empty(){ 
        header("HTTP/1.0 404 Not Found");//使HTTP返回404状态码 
        $this->assignCommon();
        $this->assign('error_reason',"(操作方法不存在)");
        $this->display("Public:error-404"); 
    }
    
    public function info(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
        
        $userModel = M("users");
        $userTable = C('DB_PREFIX').'users';
        $groupTable = C('DB_PREFIX').'usergroup';
        
        $userInfoLines = $userModel->table($userTable." u")
        ->join('LEFT JOIN '.$groupTable.' g on u.group_id=g.id')
        ->field('u.*,g.name as groupname')
        ->where('u.id='.S($authKey.":userId"))->limit(1)->select();
        
        $this->assign('userInfo', $userInfoLines[0]);
        
        $this->display();
    }
    
    public function group(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
        
        $groupTypeTable = M("usergrouptype");
        $groupTypes = $groupTypeTable->select();
        $this->assign('groupTypes', $groupTypes);
        $this->display();
    }
    
    public function systemUser(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
        
        $where = 'g.level >= '.S($authKey.":level");
        
        $groupModel = M("usergroup");
        $groupTable = C('DB_PREFIX').'usergroup';
        $groupTypeTable = C('DB_PREFIX')."usergrouptype";
        $userTable = C('DB_PREFIX').'users';
        $modelResult = $groupModel->table($groupTable." g")
        ->join('LEFT JOIN '.$groupTypeTable.' t on t.id=g.group_type')
        ->join('LEFT JOIN '.$userTable.' u on u.group_id=g.id')
        ->field("t.name as type_name, t.id as type_id, g.id as id, g.name as name, count(u.id) as count")
        ->group('g.id')->where($where)
        ->select();
        
        // LOG::write($groupModel->getLastSql());
        
        $groups = array();
        foreach($modelResult as $value){
                $groups[$value["type_name"]][]= array($value["id"], $value["name"], $value["count"], $value["type_id"]);
        }
        
        $this->assign('groups', $groups);
        $this->display();
    }
    
    public function commends(){
        $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
        
        $where = 'g.level >= '.S($authKey.":level");
        
        $groupModel = M("usergroup");
        $groupTable = C('DB_PREFIX').'usergroup';
        $groupTypeTable = C('DB_PREFIX')."usergrouptype";
        $userTable = C('DB_PREFIX').'users';
        $modelResult = $groupModel->table($groupTable." g")
        ->join('LEFT JOIN '.$groupTypeTable.' t on t.id=g.group_type')
        ->join('LEFT JOIN '.$userTable.' u on u.group_id=g.id')
        ->field("t.name as type_name, t.id as type_id, g.id as id, g.name as name, count(u.id) as count")
        ->group('g.id')->where($where)
        ->select();
        
        // LOG::write($groupModel->getLastSql());
        
        $groups = array();
        foreach($modelResult as $value){
                $groups[$value["type_name"]][]= array($value["id"], $value["name"], $value["count"], $value["type_id"]);
        }
        
        $this->assign('groups', $groups);
        $this->display();
    }
    
    public function api_adduser(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $result = array();
        if($_POST["phone"] != "" && $_POST["nickname"] != "" && $_POST["groupId"] != "" && is_numeric($_POST["groupId"])){
            $data["phone"] = $_POST["phone"];
            $data["nickname"] = $_POST["nickname"];
            $data["group_id"] = $_POST["groupId"];
            $data["password"] = MD5("888888");
            $data["parent"] = $myId;
            
            $groupModel =  M("usergroup");
            $groupLine = $groupModel->where('id='.$data["group_id"])->find();
            
            $userModel = M("users");
            $myInfo = $userModel->where('id='.$myId)->find();
            
            if($groupLine){
                if(S($authKey.":level") == null || $groupLine["level"] < S($authKey.":level")){
                    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
                }else{
                    $userModel = M("users");
                    $hasLine = $userModel->where('phone="'.$data["phone"].'"')->find();
                    if($hasLine){
                        $result = array ("state"=>104,"title"=>"操作失败","comment"=>"手机号码 [".$data["phone"]."] 已存在");
                    }else{
                        $myAssignedBrokerId = S($authKey.":userBrokerId");
                        if($myAssignedBrokerId == null && false) {
                            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"请重新登录");
                        }else{
                            $myAssignedBrokerId = $myInfo["orgn_broker"];
                            $data["orgn_broker"] = $myAssignedBrokerId;
                            
                            $userModel->add($data);
                            $result = array ("state"=>200,"title"=>"操作成功","comment"=>"添加用户 [".$data["nickname"]."] 成功");
                        }
                    }
                }
            }
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"参数丢失");
        }
        print json_encode($result);
    }
    
    public function api_addcustomer(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $_boxId = $_POST["boxid"];
        $_phone = $_POST["phone"];
        $_groupId = $_POST["groupId"];
        
        $result = array();
        if($_phone != "" && $_boxId != "" 
        && $_groupId != "" && is_numeric($_groupId)){
            $data["login_name"] = $_phone;
            $data["group_id"] = $_groupId;
            $data["password"] = MD5("888888");
            $data["owner"] = S($authKey.":userId");
            
            $myAssignedBrokerId = S($authKey.":userBrokerId");
            if($myAssignedBrokerId == null) {
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"请重新登录");
                print json_encode($result);
                exit;
            }else{
                $data["orgn_broker"] = $myAssignedBrokerId;
            }
            
            $boxModel = M("user_box");
            $hasBox = $boxModel->field("brokerId,user_id")->where('box_name="'.$_boxId.'"')->limit(1)->select();
            if(count($hasBox) < 1){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"盒子号码不存在.");
                print json_encode($result);
                exit;
            }else{
                if($hasBox[0]["user_id"] != 0){
                    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"盒子号码已被另外的账户绑定.");
                    print json_encode($result);
                    exit;
                }
                $boxBrokerId = $hasBox[0]["brokerId"];
                if($this->hasBrokerPrivilege($boxBrokerId) == false){
                    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"无操作权限.");
                    print json_encode($result);
                    exit;
                }
            }
            
            $groupModel =  M("usergroup");
            $groupLine = $groupModel->where('id='.$data["group_id"])->limit(1)->select();
            if(count($groupLine) < 1){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组不存在.");
            }else{
              if(S($authKey.":level") == null || $groupLine[0]["level"] <= S($authKey.":level")){
                  $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
              }else{
                $userModel = M("users");
                $hasLine = $userModel->where('login_name="'.$data["login_name"].'"')->limit(1)->select();
                    if(count($hasLine) == 0){
                        $newUserId = $userModel->add($data);
                      
                        $boxModel = M("user_box");
                        $boxData["user_id"] = $newUserId;
                        $boxData["active_time"] = date('Y-m-d H:i:s', time());
                        
                        $boxModel->where('box_name="'.$_boxId.'"')->save($boxData);
                      
                        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"添加用户 [".$data["login_name"]."] 成功", "userId"=>$newUserId);
                    }else{
                        $result = array ("state"=>104,"title"=>"操作失败","comment"=>"登录名 [".$data["login_name"]."] 已存在");
                    }
                }
            }
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"参数丢失");
        }
        print json_encode($result);
    }
    
    public function api_addusergroup(){
        auth(__CLASS__,__FUNCTION__);
        if($_POST["groupName"] != ""){
            $data["name"] = $_POST["groupName"];
            $data["group_type"] = $_POST["groupTypeId"];
            $data["level"] = $_POST["groupLevel"];
            $userGroupTable = M("usergroup");
            $hasLine = $userGroupTable->where('name="'.$data["name"].'"')->limit(1)->select();
            if(count($hasLine) == 0){
                $userGroupTable->add($data);
                $result = array ("state"=>200,"title"=>"操作成功","comment"=>"添加用户组 [".$data["name"]."] 成功");
                print json_encode($result);
            }else{
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组 [".$data["name"]."] 已存在");
                print json_encode($result);
            }
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组名称不能为空");
            print(json_encode($result));
        }
    }
    
    public function api_getusergroup_list(){
        auth(__CLASS__,__FUNCTION__);
        $list = $this->getusergroup_list();
        $result = array ("state"=>200,"userGroupList"=>$list);
        print(json_encode($result));
    }
    
    private function getusergroup_list(){
        $userGroupTable = M("usergroup");
        $groupTable = C('DB_PREFIX').'usergroup';
        $groupTypeTable = C('DB_PREFIX').'usergrouptype';
        $prvTable = C('DB_PREFIX').'group_privileges';
        $apiTable = C('DB_PREFIX').'controller_api';
        
        $userGroupList = $userGroupTable->table($groupTable." g")
        ->join('LEFT JOIN '.$apiTable.' pg on g.default_page_id=pg.id')
        ->join('LEFT JOIN '.$prvTable.' p on g.id=p.group_id')
        ->join('LEFT JOIN '.$groupTypeTable.' t on t.id=g.group_type')
        ->field('g.id, g.name, g.locked, pg.show_name as default_api_name, count(p.api_id) as privileges, t.name as type_name, g.level as level, g.default_page_id as default_page')
        ->group('g.id')
        ->select();
        
        //$sql = $userGroupTable->getLastSql();
        
        return $userGroupList;
    }
    
    public function api_getuser_list(){
        auth(__CLASS__,__FUNCTION__);
        $groupId = I('path.2');
        $authKey = $_COOKIE['authKey'];
        if($groupId == "" || $authKey == "") return;
        
        $groupTable =  M("usergroup");
        $groupLine = $groupTable->where('id='.$groupId)->limit(1)->select();
        $result = array ();
        if(count($groupLine) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组不存在.");
        }else{
          if((S($authKey.":level") == null || $groupLine[0]["level"] < S($authKey.":level"))){
              $comment = "权限不足.";
              $result = array ("state"=>104,"title"=>"操作失败","comment"=>$comment);
          }else{
              $userTable = M("users");
              $userList = $userTable
              ->where("group_id=".$groupId)
              ->field("id,phone,nickname,email,create_date,locked, group_id, parent")
              ->select();
              
              $result = array ("state"=>200,"userList"=>$userList);
          }
        }
        
        print(json_encode($result));
    }
    
    public function api_getcommend_list(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $groupId = I('path.2');
        $authKey = $_COOKIE['authKey'];
        if($groupId == "" || $authKey == "") return;
        
        $groupTable =  M("usergroup");
        $groupLine = $groupTable->where('id='.$groupId)->limit(1)->select();
        $result = array ();
        if(count($groupLine) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组不存在.");
        }else{
          if((S($authKey.":level") == null || $groupLine[0]["level"] < S($authKey.":level"))){
              $comment = "权限不足.";
              $result = array ("state"=>104,"title"=>"操作失败","comment"=>$comment);
          }else{
              $userTable = M("users");
              $userList = $userTable
              ->where("group_id=".$groupId." AND parent=".$myId)
              ->field("id,phone,nickname,email,create_date,locked, sms_price, sms_account")
              ->select();
              
              $result = array ("state"=>200,"userList"=>$userList);
          }
        }
        
        print(json_encode($result));
    }
    
    public function api_getprivilege_list(){
        auth(__CLASS__,__FUNCTION__);
        $groupId = I('path.2');
        if($groupId == "") return;
        
        $apiTable = C('DB_PREFIX').'controller_api';
        $privilegeTable = C('DB_PREFIX').'group_privileges';
        
        $operationTable = M("controller_api");
        $apiList = $operationTable->table($apiTable." a")
        ->join('LEFT JOIN '.$privilegeTable.' p on a.id=p.api_id and p.group_id='.$groupId)
        ->field('a.id, a.function_name, a.show_name, a.show_in_left_menu, a.parent_id, a.sequence_level, p.group_id')
        ->limit(200)->select();
        
        $result = array ("state"=>200,"apiList"=>$apiList);
        print(json_encode($result));
    }
    
    public function api_group_has_user(){
        auth(__CLASS__,__FUNCTION__);
        $groupId = I('path.2');
        if($groupId == "") return;
        
        $userTable = M("users");
        $userList = $userTable
        ->where("group_id=".$groupId)->select();
        
        $groupTable = M("usergroup");
        $locked = $groupTable->field("locked")->where("id=".$groupId)->limit(1)->select();
        
        $result = array ("state"=>200,"hasUser"=>count($userList),"locked"=>$locked[0]["locked"]);
        print(json_encode($result));
    }
    
    public function api_reset_user_psw(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $targetUserId = I('path.2');
        if($targetUserId == "" || $authKey == "") return;
        
        $userModel = M("users");
        $userTable = C('DB_PREFIX').'users';
        $groupTable = C('DB_PREFIX').'usergroup';
        
        $userList = $userModel->table($userTable." u")
        ->join('LEFT JOIN '.$groupTable.' g on u.group_id=g.id')
        ->field('g.level as level')
        ->where("u.id=".$targetUserId)->limit(1)->select();
        
        $result = "";
        if(count($userList) < 1){
             $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户不存在.");
        }else{
            if(S($authKey.":level") == null || $userList[0]["level"] <= S($authKey.":level")){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
            }else{
                $data["password"] = MD5("888888");
                $userModel->where('id='.$targetUserId)->save($data);
                $result = array ("state"=>200,"title"=>"操作成功","comment"=>"密码重设成功.");
            }
        }
        print(json_encode($result));
    }
    
    
    public function api_charge(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $user = $_POST["user"];
        $money = $_POST["money"];
        
        $userModel = M("users");
        
        $userInfo = $userModel->where("id=".$user)->find();
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"充值成功.");
        if($userInfo){
            $oldMoney = $userInfo["sms_account"];
            $newMoney = $oldMoney + $money;
            $data = array();
            $data["sms_account"] = $newMoney;
            $userModel->where("id=".$user)->save($data);
            
            $recordModel = M("charge_record");
            $data = array();
            $data["operator"] = $myId;
            $data["for_user"] = $user;
            $data["add_money"] = $money;
            $data["final_money"] = $newMoney;
            
            $recordModel->add($data);
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户不存在.");
        }
        print(json_encode($result));
    }
    
    public function api_money_transfer(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $user = $_POST["user"];
        $money = $_POST["money"];
        
        $userModel = M("users");
        
        $myInfo = $userModel->field("sms_account")->where("id=".$myId)->find();
        $userInfo = $userModel->where("id=".$user)->find();
        
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"充值成功.");
        if($userInfo){
            if($myInfo["sms_account"] < $money){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"本帐户余额不足.");
                print(json_encode($result));
                return;
            }
            
            $myNewMoney = $myInfo["sms_account"] - $money;
            $data = array();
            $data["sms_account"] = $myNewMoney;
            $userModel->where("id=".$myId)->save($data);
            
            $oldMoney = $userInfo["sms_account"];
            $newMoney = $oldMoney + $money;
            $data = array();
            $data["sms_account"] = $newMoney;
            $userModel->where("id=".$user)->save($data);
            
            $recordModel = M("charge_record");
            $data = array();
            $data["operator"] = $myId;
            $data["for_user"] = $user;
            $data["add_money"] = $money;
            $data["final_money"] = $newMoney;
            $data["reason"] = 2;  // 转账收入
            
            $recordModel->add($data);
            
            $data = array();
            $data["operator"] = $myId;
            $data["for_user"] = $user;
            $data["add_money"] = 0 - $money;
            $data["final_money"] = $myNewMoney;
            $data["reason"] = 3;  // 转账支出
            
            $recordModel->add($data);
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户不存在.");
        }
        print(json_encode($result));
    }
    
    public function api_change_usergroup(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $targetUserId = I('path.2');
        $targetGroupId = I('path.3');
        if($targetUserId == "" || $targetGroupId == "" || $authKey == "") return;
        
        $userModel = M("users");
        $groupModel = M("usergroup");
        $userTable = C('DB_PREFIX').'users';
        $groupTable = C('DB_PREFIX').'usergroup';
        
        $userList = $userModel->table($userTable." u")
        ->join('LEFT JOIN '.$groupTable.' g on u.group_id=g.id')
        ->field('g.level as level')
        ->where("u.id=".$targetUserId)->limit(1)->select();
        
        $result = "";
        if(count($userList) < 1){
             $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户不存在.");
        }else{
            if((S($authKey.":level") == null || $userList[0]["level"] < S($authKey.":level")) 
              && S($authKey.":groupId") != 1){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
            }else{
                $groupLine = $groupModel->where('id='.$targetGroupId)
                ->field('level')->limit(1)->select();
                if(count($groupLine) < 1){
                    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户组不存在.");
                }elseif($groupLine[0]["level"] < S($authKey.":level") && S($authKey.":groupId") != 1){
                    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
                }else{
                    $data["group_id"] = $targetGroupId;
                    $userModel->where('id='.$targetUserId)->save($data);
                    $result = array ("state"=>200,"title"=>"操作成功","comment"=>"用户调组成功.");
                }
            }
        }
        print(json_encode($result));
    }
    
    public function api_copy_privilege(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $from = $_POST["from"];
        $to = $_POST["to"];
        if($from == "" || $to == "" || $authKey == "") return;
        $myLevel = S($authKey.":level");
        
        $groupModel = M("usergroup");
        $fromGroup = $groupModel->where("id=".$from)->find();
        
        if($fromGroup){
            if($fromGroup["level"] < $myLevel){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
                print(json_encode($result));
                exit;
            }
        } else exit;
        
        $toGroup = $groupModel->where("id=".$to)->find();
        if($toGroup){
            if($toGroup["level"] < $myLevel){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
                print(json_encode($result));
                exit;
            }
            if($toGroup["locked"] == 1){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"目标用户组被锁定.");
                print(json_encode($result));
                exit;
            }
        } else exit;
        
        $privilegeModel = M("group_privileges");
        
        $privilegeModel->where("group_id=".$to)->delete();
        $fromList = $privilegeModel->where("group_id=".$from)->select();
        
        $data = array();
        $data["group_id"] = $to;
        foreach($fromList as $fromTuple){
            $data["api_id"] = $fromTuple["api_id"];
            $privilegeModel->add($data);
        }
        
        $result = array ("state"=>200,"title"=>"复制成功","comment"=>"用户权限已复制.");
        print(json_encode($result));
    }
    
    public function api_delete_group(){
        $groupId = I('path.2');
        if($groupId == "") return;
        
        $groupTable = M("usergroup");
        $groupTable->where("id=".$groupId)->delete();
        
        $privilegeTable = M("group_privileges");
        $privilegeTable->where("group_id=".$groupId)->delete();
        
        $result = array ("state"=>200,"title"=>"删除成功","comment"=>"用户组已删除");
        print(json_encode($result));
    }
    
    public function api_toggle_user(){
        auth(__CLASS__,__FUNCTION__);
        $authKey = $_COOKIE['authKey'];
        $userId = I('path.2');
        if($userId == "" || $authKey == "") return;
        
        $userModel = M("users");
        $userTable = C('DB_PREFIX').'users';
        $groupTable = C('DB_PREFIX').'usergroup';
        
        $userList = $userModel->table($userTable." u")
        ->join('LEFT JOIN '.$groupTable.' g on u.group_id=g.id')
        ->field('g.level as level, u.locked as locked')
        ->where("u.id=".$userId)->limit(1)->select();
        
        $result = array ();
        if(count($userList) < 1){
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"用户不存在");
        }else{
            if(S($authKey.":level") == null || $userList[0]["level"] <= S($authKey.":level")){
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"权限不足.");
            }else{
                $data["locked"] = 1 - $userList[0]["locked"];
                $userModel->where('id='.$userId)->save($data);
                $result = array ("state"=>200,"title"=>"操作成功","comment"=>"用户设置成功.");
            }
        }
        
        print(json_encode($result));
    }
    
    public function api_modify_privilege(){
        auth(__CLASS__,__FUNCTION__);
        $groupId = $_POST["groupId"];
        $add = $_POST["add"];
        $del = $_POST["del"];
        
        $privilegeModel = M("group_privileges");
        
        $addParts = explode("|",$add);
        $delParts = explode("|",$del);
        
        //$addCount = $addParts[0];
        
        $addRecord = array();
        $delRecord = array();
        foreach($addParts as $api){
            if($api != "") {
                $hasTuple = $privilegeModel->where("group_id=".$groupId." and api_id=".$api)->limit(1)->select();
                $addCount = count($hasTuple);
                if(count($hasTuple) == 0){
                    $data["group_id"] = $groupId;
                    $data["api_id"] = $api;
                    $privilegeModel->add($data);
                    $addRecord[] = $api;
                }
            }
        }
        
        foreach($delParts as $api){
            if($api != "") {
                $privilegeModel->where("group_id=".$groupId." and api_id=".$api)->delete();
                $delRecord[] = $api;
            }
        }
        // refresh cache
        refreshGroupPrivilegeCache($groupId);
        
        $result = array ("state"=>200,"title"=>"修改成功","comment"=>"用户组权限修改成功.",
        "groupId"=>$groupId,"add"=>$addRecord,"del"=>$delRecord,"addval"=>$add,"delval"=>$del,"addCount"=>$addCount);
        print(json_encode($result));
    }
    
    public function api_info_change(){
        $authKey = $_COOKIE['authKey'];
        
        $userData = array();
        if(isset($_POST["form-nick-name"])) $userData["nickname"] = $_POST["form-nick-name"];
        if(isset($_POST["form-email"])) $userData["email"] = $_POST["form-email"];
        if(isset($_POST["form-sms"])) $userData["sms"] = $_POST["form-sms"];
        
        $userModel = M("users");
        
        if(count($userData) > 0) $result = $userModel->where('id='.S($authKey.":userId"))->save($userData);
        
        $returnVal = array();
        if($result !== false) {
          $returnVal = array ("state"=>200,"title"=>"操作成功","comment"=>"用户个人信息修改成功.");
          if(isset($_POST["form-nick-name"])) S($authKey.":showName",$_POST["form-nick-name"],C('CACHE_USER_INFO_SECOND'));
          S($authKey.":infoCompletion",null);
        }else{
          $returnVal = array ("state"=>104,"title"=>"操作失败","comment"=>"请再次尝试操作.");
        }
        print(json_encode($returnVal));
    }
    
    public function api_password_change(){
        $authKey = $_COOKIE['authKey'];
        
        $data = array();
        $returnVal = array();
        $userModel = M("users");
        $_POST["cp-form-original-password"] = strtolower($_POST["cp-form-original-password"]);
        $_POST["cp-form-new-password"] = strtolower($_POST["cp-form-new-password"]);
        if($_POST["cp-form-original-password"] != "") {
            $getUser = $userModel->where('id='.S($authKey.":userId"))->limit(1)->select();
            if(count($getUser) < 1){
                $returnVal = array ("state"=>104,"title"=>"操作失败","comment"=>"用户登录信息过期，请重新登录。");
            }else if($getUser[0]["password"] == $_POST["cp-form-original-password"]){
                $data["password"] = $_POST["cp-form-new-password"];
                $result = $userModel->where('id='.S($authKey.":userId"))->save($data);
                if($result !== false) {
                  $returnVal = array ("state"=>200,"title"=>"操作成功","comment"=>"用户密码修改成功.");
                }else{
                  $returnVal = array ("state"=>104,"title"=>"操作失败","comment"=>"请再次尝试操作.");
                }
            }else{
                $returnVal = array ("state"=>104,"title"=>"操作失败","comment"=>"原密码不正确.");
            }
        }
        print(json_encode($returnVal));
    }
    
    public function api_get_status(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        
        $userModel = M("users");
        $userInfo = $userModel->field("sms_account")->where("id=".$myId)->find();
        
        $returnVal = array ("state"=>200, "sms_account"=>$userInfo["sms_account"]);
        print(json_encode($returnVal));
    }
    /*
    public function getUserInfo($uid){
        auth(__CLASS__,__FUNCTION__);
        $userTable = M("user");
        $userInfo = $userTable->where('id='.$uid)->limit(1)->select();
        if(count($userInfo) > 0) return $userInfo[0];
        return null;
    }
    */
    
    private function assignCommon(){
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        $this->assign('userName', S($authKey.":showName"));
        $this->assign('webroot', C("WEB_ROOT"));
        $this->assign('sitename', C("SITE_NAME"));
        $completion = S("user:".$myId.":infoCompletion");
        if($completion == null || $completion == ""){
            $this->checkUserInfoCompletion();
            $completion = S("user:".$myId.":infoCompletion");
        }
        $this->assign('infoCompleteJson', $completion);
        
        $informArr = S("user:".$myId.":inform");
        if($informArr == null) $informArr = "[]";
        $this->assign('informJson', $informArr);
        
        $userModel = M("users");
        $queryList = $userModel->select();
        $userDict = array();
        foreach($queryList as $value){
            $userDict[$value["id"]] = $value["nickname"];
        }
        
        $this->assign('userDict', json_encode($userDict));
        $this->assign('callResultDict', json_encode(C("CALL_STATUS")));
        $this->assign('caseResultDict', json_encode(C("FOLLOW_STATUS")));
    }
    
    public function checkUserInfoCompletion(){  // for interval invoke
        $authKey = $_COOKIE['authKey'];
        $myId = S($authKey.":userId");
        if($myId != null && $myId != ""){
            $userModel = M("users");
            
            $userInfoLines = $userModel->where('id='.$myId)->limit(1)->select();
            
            $userInfo = $userInfoLines[0];
              
            $jsonResult = array();
                
            if($userInfo["nickname"] == null || $userInfo["nickname"] == ""){
                $jsonResult[] = "昵称未设置";
            }
            if($userInfo["email"] == null || $userInfo["email"] == ""){
                $jsonResult[] = "电子邮箱未设置(不可用邮箱登录)";
            }
            
            $authKey = $_COOKIE['authKey'];
            $jsonString = json_encode($jsonResult);
            S("user:".$myId.":infoCompletion",$jsonString,C('CACHE_USER_INFO_SECOND'));
        }
    }
    
    private function dayGap($sourceTimeStamp, $targetTimeStamp){
        //LOG::write("dayGap: source:".$sourceTimeStamp." target:".$targetTimeStamp);
        $secondGap = $targetTimeStamp - $sourceTimeStamp;
        $dayGap = floor($secondGap/(60*60*24));
        return $dayGap;
    }
    
    private function hasBrokerPrivilege($targetBrokerId){
        $authKey = $_COOKIE['authKey'];
        $myAssignedBrokerId = S($authKey.":userBrokerId");
        if($myAssignedBrokerId == null) return false;
        if($myAssignedBrokerId == $targetBrokerId) return true;
        $brokerModel = M("brokergroup");
        $result = $this->subBrokerFinding($brokerModel,$myAssignedBrokerId,$targetBrokerId);
        return $result;
    }
    
    private function subBrokerFinding($model,$curBroker,$tarBroker){
        $result = false;
        $subBrokers = $model->field("id")->where("parent_id=".$curBroker)->select();
        for($i=0;$i<count($subBrokers) && !$result;$i++){
          if($subBrokers[$i]["id"] == $tarBroker) $result = true;
          if(!$result) $result = $this->subBrokerFinding($model,$subBrokers[$i]["id"],$tarBroker);
        }
        return $result;
    }
    
    private function checkEmailFormat($email){
        if (ereg("^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(\.[a-zA-Z0-9_-])+",$email)) {
            return true;
        }
        return false;
    }
}

?>