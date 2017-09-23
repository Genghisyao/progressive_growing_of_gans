<?php
namespace Home\Controller;
use Think\Controller;

class ContentController extends Controller {
    public function index(){
	    $this->assign('sideMenu',auth(__CLASS__,__FUNCTION__));
        $this->assignCommon();
        $authKey = $_COOKIE['authKey'];
		
		$myBrokderId = S($authKey.":userBrokerId");
		$myId = S($authKey.":userId");
		
		$cGroupModel = M("contentgroup");
		$cGroupList = $cGroupModel->where("broker_id=".$myBrokderId)->select();
		$this->assign('groups', $cGroupList);
	
	    $this->display();
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