<?php
return array(
  'DB_TYPE' => 'mysql',
  'DB_HOST' => 'localhost',
  'DB_NAME' => 'sentiment',
  'DB_USER' => 'yqfx',
  'DB_PWD' => 'yqfx',
  'DB_PREFIX' => '',
  'CACHE_USER_INFO_SECOND' => 2160000,
  'SITE_NAME' => '平安',
  'SITE_DOMAIN_NAME' => 'nehouse-w.carslink.net',
  'RPC_SERVER' => 'localhost',
  
  'WEB_ROOT' => '/',
  
  'TOKEN' => 'weixin',
  'APPID' => 'wx97db2b64ecf92068',
  'APPSECRET' => '8ab6452d64a008e0448d57855cdf2511',
  'PUBLIC_OPEN_ID' => 'gh_fecf654f6ee6',
  
  'REDIS_HOST' => '112.124.47.197',
  'REDIS_PORT' => 6379,
  
  'SMS_INTERFACE' => array(
      'sms82' => array(
          'key' => 'sms82',
          'name' => '通知接口82',
          'sendAction' => 'channelSendVia82'
      ),
      'sms178' => array(
          'key' => 'sms178',
          'name' => '营销接口178',
          'sendAction' => 'channelSendVia178'
      ),
      'sms52' => array(
          'key' => 'sms52',
          'name' => '移动接口52',
          'sendAction' => 'channelSendVia52'
      )
  ),
   
    
  
  //'DATA_CACHE_TYPE' => 'Memcached',
  /*
  'DATA_CACHE_TYPE'                   => 'Redis',
  'REDIS_HOST'                        => '112.124.47.197',
  'REDIS_PORT'                        => 6379,
  'DATA_CACHE_TIME'                   => 3600,
  
  'DATA_CACHE_PREFIX' => 'wxpub:',
  'PERSISTENTID' => 'tp',// optional
   'MEMCACHED_HOST' => array('127.0.0.1'),
  // 'MEMCACHED_HOST' => array('713bb48261bb11e3.m.cnhzalicm10pub001.ocs.aliyuncs.com'),
  'MEMCACHED_PORT' => array('11211'),
  // 'MEMECACHED_WEIGHT' => array(33,67),// optional
  */
);
 

?>