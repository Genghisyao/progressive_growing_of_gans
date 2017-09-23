<?php
namespace Home\Controller;
use Think\Controller;

class MenuController extends Controller {
    public function index(){
	    $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
		
		$myBrokderId = S($authKey.":userBrokerId");
		$myId = S($authKey.":userId");
		
		$cGroupModel = M("contentgroup");
		$cGroupList = $cGroupModel->where("broker_id=".$myBrokderId)->select();
		$this->assign('groups', $cGroupList);
        
        $menuModel = M("menu");
        $menus = $menuModel->order("id")->select();
        $this->assign('menus', $menus);
	
	    $this->display();
    }
    
    public function dummy(){
    }
    
    public function api_get_saved_menu(){
        $id = $_GET["_URL_"][2];
        $menuModel = M("menu");
        
        $menuTuple = $menuModel->where("id=".$id)->find();
        if($menuTuple){
            $jsonObj = json_decode($menuTuple["menu_string"], true);
            $result = array ("state"=>200,"title"=>"操作成功","comment"=>$jsonObj);
        }else{
            $result = array ("state"=>104,"title"=>"操作失败","comment"=>"没有找到菜单数据.");
        }
        print(json_encode($result));
    }
    
    public function api_get_menu(){
        //$jsonStr = '{"menu":{"button":[{"type":"click","name":"Songs","key":"GET_CONTENT_2","sub_button":[]},{"type":"click","name":"Singers","key":"GET_GROUP_5","sub_button":[]},{"name":"Menu","sub_button":[{"type":"view","name":"search","url":"http://www.soso.com/","sub_button":[]},{"type":"view","name":"Viedo","url":"http://v.qq.com/","sub_button":[]},{"type":"click","name":"Good","key":"V1001_GOOD","sub_button":[]}]}]}}';
        $WxioObj = A('Wxio');
		$jsonObj = $WxioObj->api_getMenu();
        //$jsonObj = json_decode($jsonStr);
        
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>$jsonObj);
        print(json_encode($result));
    }
    
    public function api_save_menu(){
        $WxioObj = A('Wxio');
		$jsonObj = $WxioObj->api_getMenu();
        $jsonStr = json_encode($jsonObj);
        
        $menuModel = M("menu");
        $data = array();
        $data["menu_string"] = $jsonStr;
        $menuModel->add($data);
        
        //LOG::write($jsonStr);
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"当前服务器上的微信菜单已保存.");
        print(json_encode($result));
    }
    
    private function unicode_encode($str, $encoding = 'GBK', $prefix = '&#', $postfix = ';') {
        $str = iconv($encoding, 'UCS-2', $str);
        $arrstr = str_split($str, 2);
        $unistr = '';
        for($i = 0, $len = count($arrstr); $i < $len; $i++) {
            $dec = hexdec(bin2hex($arrstr[$i]));
            $unistr .= $prefix . $dec . $postfix;
        } 
        return $unistr;
    } 
    
    private function unicode_decode($unistr, $encoding = 'GBK', $prefix = '\u', $postfix = ';') {
        $arruni = explode($prefix, $unistr);
        $unistr = '';
        for($i = 1, $len = count($arruni); $i < $len; $i++) {
            if (strlen($postfix) > 0) {
                $arruni[$i] = substr($arruni[$i], 0, strlen($arruni[$i]) - strlen($postfix));
            } 
            $temp = intval($arruni[$i]);
            $unistr .= ($temp < 256) ? chr(0) . chr($temp) : chr($temp / 256) . chr($temp % 256);
        } 
        return iconv('UCS-2', $encoding, $unistr);
    }
    
    public function api_set_menu(){
        // ** for debug  ** //
        $obj["GET"] = $_GET;
        $obj["POST"] = $_POST;
        $obj["state"] = 200;
        
		var_dump($obj["POST"]);
		//LOG::write($resultStr,LOG::DEBUG);
        //print($resultStr);
        // ** debug end  ** //
        
        
        // ** logic start  ** //
        $dataStr = $_POST["data"];
        $dataArray_0 = json_decode($dataStr, true);
		//print " dataArray is: ";
		//print " name: ".$dataArray[2]["sub_button"][0]["name"];
		//if(isset($dataArray[2]["sub_button"])){
		//    $subMenu = $dataArray[2]["sub_button"];
		$arrMenu = array();
		$arrButton = array();
        foreach ($dataArray_0 as $k_0=>$val_0) {
			$strDebug = "";
			$arrMenu_0 = array();
			$arrMenu_0["name"] = $val_0["name"];
			if ( isset($val_0["mType"])) {
				$strDebug = $strDebug." name: ".$val_0["name"].", mType: ".$val_0["mType"];
				$arrMenu_0["type"] = $val_0["mType"];
				if (isset($val_0["mPara"])) {
					$strDebug = $strDebug.", mPara: ".$val_0["mPara"];
					$arrMenu_0["key"] = $val_0["mPara"];
				}
				if ($val_0["mType"] == "view") {  //find "view"
					if (isset($val_0["parameter"])) {
						$strDebug = $strDebug.", parameter: ".$val_0["parameter"];
						$arrMenu_0["url"] = $val_0["parameter"];
					}					
				}
				$arrButton[] =	$arrMenu_0;					
			} else { // it is a sub-menu
				$strDebug = $strDebug." name: ".$val_0["name"].",sub-menu: \n";
				if (isset($val_0["sub_button"])) {
					$dataArray_1 = $val_0["sub_button"];
					$arrSubButton = array();
					$arrMenu_1 = array();
					foreach ($dataArray_1 as $k_1=>$val_1) {
						$strDebug = $strDebug."\n name: ".$val_1["name"];
						$strDebug = $strDebug.", mType: ".$val_1["mType"];
						$arrMenu_1["name"] = $val_1["name"];
						$arrMenu_1["type"] = $val_1["mType"];
						if (isset($val_1["mPara"])) {
							$strDebug = $strDebug.", mPara: ".$val_1["mPara"];
							$arrMenu_1["key"] = $val_1["mPara"];
						}
						if ($val_1["mType"] == "view") {  //find "view"
							if (isset($val_1["parameter"])) {
								$strDebug = $strDebug.", parameter: ".$val_1["parameter"];
								$arrMenu_1["url"] = $val_1["parameter"];
							}						
						}
						$arrSubButton[] = $arrMenu_1; //添加子目录
					}
					$arrMenu_0["sub_button"] = $arrSubButton;
					$arrButton[] =	$arrMenu_0;
				} else {
					LOG::write("Error on sub-menu",LOG::DEBUG);
				}				
			}
			//LOG::write(" menu : ".$strDebug,LOG::DEBUG);	
		}
		$arrMenu["button"] = $arrButton;
		//LOG::write(" menu on array is : ".json_encode($arrMenu),LOG::DEBUG);	
		//print($dataArray);
        
		$WxioObj = A('Wxio');
		$WxioObj->api_createMenu($arrMenu);
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"菜单已保存到微信服务器.");
        print(json_encode($result));
    }
	
	public function api_addgroup(){
	    auth(__CLASS__,__FUNCTION__);
		
		if(!isset($_POST["groupName"]) || $_POST["groupName"] == ""){
		    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"数据丢失.");
		    print(json_encode($result));
			exit;
		}
		
		
        $authKey = $_COOKIE['authKey'];
		$myBrokderId = S($authKey.":userBrokerId");
		$myId = S($authKey.":userId");
		
		$cGroupModel = M("contentgroup");
		$data = array();
		$data["name"] = $_POST["groupName"];
		$data["broker_id"] = $myBrokderId;
		
		$newId = $cGroupModel->add($data);
		
		$result = array ("state"=>200,"title"=>"操作成功","comment"=>"栏目增加成功.","id"=>$newId);
		print(json_encode($result));
    }
	
	public function api_editgroup(){
	    auth(__CLASS__,__FUNCTION__);
		
		if(!isset($_POST["groupName"]) || $_POST["groupName"] == ""
		|| !isset($_POST["id"]) || $_POST["id"] == ""){
		    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"数据丢失.");
		    print(json_encode($result));
			exit;
		}
		
		
        $authKey = $_COOKIE['authKey'];
		$myBrokderId = S($authKey.":userBrokerId");
		
		$cGroupModel = M("contentgroup");
		$data = array();
		$data["name"] = $_POST["groupName"];
		$gid = $_POST["id"];
		
		$result = array();
		$oldDataList = $cGroupModel->where("id=".$gid)->limit(1)->select();
		if(count($oldDataList) > 0 && $oldDataList[0]["broker_id"] == $myBrokderId){
		    $cGroupModel->where("id=".$gid)->limit(1)->save($data);
		    $result = array ("state"=>200,"title"=>"操作成功","comment"=>"栏目修改成功.");
		}else{
		    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"无数据.");
		}
		print(json_encode($result));
    }
	
	public function api_delgroup(){
	    auth(__CLASS__,__FUNCTION__);
		
		if(!isset($_POST["id"]) || $_POST["id"] == ""){
		    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"数据丢失.");
		    print(json_encode($result));
			exit;
		}
		
		
        $authKey = $_COOKIE['authKey'];
		$myBrokderId = S($authKey.":userBrokerId");
		
		$cGroupModel = M("contentgroup");
		$gid = $_POST["id"];
		
		$result = array();
		
		$contentModel = M("content");
		$hasContent = $contentModel->where("group_id=".$gid)->limit(1)->select();
		
		if(count($hasContent) > 0){
		    $result = array ("state"=>104,"title"=>"删除失败","comment"=>"栏目下有发布文章.");
		}else{
		    $oldDataList = $cGroupModel->where("id=".$gid)->limit(1)->select();
		    if(count($oldDataList) > 0 && $oldDataList[0]["broker_id"] == $myBrokderId){
		        $cGroupModel->where("id=".$gid)->delete();
		        $result = array ("state"=>200,"title"=>"操作成功","comment"=>"栏目已删除.");
		    }else{
		        $result = array ("state"=>104,"title"=>"操作失败","comment"=>"无数据.");
		    }
		}
		print(json_encode($result));
    }
	
	public function api_content_table_interface(){
	    auth(__CLASS__,__FUNCTION__);
		
		$authKey = $_COOKIE['authKey'];
		$myBrokderId = S($authKey.":userBrokerId");
		$myId = S($authKey.":userId");
        
        $contentModel = M("content");
        if($_POST["oper"] == "del"){
            if(isset($_POST["id"])){
                $hasLine = $contentModel->where("id=".$_POST["id"])->limit(1)->select();
                if(count($hasLine) > 0 && $hasLine[0]["broker_id"] == $myBrokderId){
                    $contentModel->where("id=".$_POST["id"])->limit(1)->delete();
                    $result = array ("state"=>200,"title"=>"操作成功","comment"=>"文章已删除.");
                    print(json_encode($result));
			        exit;
                }
            }else{
                $result = array ("state"=>104,"title"=>"操作失败","comment"=>"数据不完整.");
		        print(json_encode($result));
			    exit;
            }
        }
		
		if(!isset($_POST["title"]) || !isset($_POST["pic"])
		|| !isset($_POST["abs"]) || !isset($_POST["mceArea"]) || !isset($_POST["cgroup"])){
		    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"数据丢失.");
		    print(json_encode($result));
			exit;
		}
		
		$data = array();
		$data["title"] = $_POST["title"];
		$data["abstract"] = $_POST["abs"];
		$data["content"] = $_POST["mceArea"];
		$data["cover"] = $_POST["pic"];
		$data["group_id"] = $_POST["cgroup"];
		$data["user_id"] = $myId;
        
		$result = array();
        if($_POST["oper"] == "add"){
		    $data["broker_id"] = $myBrokderId;
		    $contentModel->add($data);
		    
		    $result = array ("state"=>200,"title"=>"操作成功","comment"=>"文章已添加.");
        }else if($_POST["oper"] == "edit"){
            $oper_content_id = $_POST["oper_content_id"];
            
			$hasContent = $contentModel->where("id=".$oper_content_id)->limit(1)->select();
			
			if(count($hasContent) > 0){
			    if($hasContent[0]["broker_id"] == $myBrokderId){
				    $contentModel->where("id=".$oper_content_id)->limit(1)->save($data);
					$result = array ("state"=>200,"title"=>"操作成功","comment"=>"文章已更改.");
				}else{
				    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"无操作权限.");
				}
			}else{
			    $result = array ("state"=>104,"title"=>"操作失败","comment"=>"文章不存在.");
			}
        }
        
		print(json_encode($result));
	}
	
	public function api_get_contentlist(){
        auth(__CLASS__,__FUNCTION__);
        $groupId = $_GET["_URL_"][2];
        
        $authKey = $_COOKIE['authKey'];
		$myBrokderId = S($authKey.":userBrokerId");
        
        $contentModel = M("content");
        $contentTable = C('DB_PREFIX').'content';
        $groupTable = C('DB_PREFIX').'contentgroup';
        
        $contentList = $contentModel->table($contentTable." c")
        ->join($groupTable.' g on g.id=c.group_id')
        ->field("c.*,g.name as gname")
        ->where("c.broker_id=".$myBrokderId." AND c.group_id=".$groupId)->select();
        
        $result = array ("state"=>200,"title"=>"操作成功","comment"=>$contentList);
		print(json_encode($result));
    }
    
	private function assignCommon(){
        $authKey = $_COOKIE['authKey'];
        $this->assign('userName', S($authKey.":showName"));
		$this->assign('webroot', C("WEB_ROOT"));
    }
}
?>