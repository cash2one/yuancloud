window.onload = function() {
    //alert(1);
         wxGetSign();
 };
         // 配置数据
wxConfigData={
    debug: false, //调试的时候最好设为true，它每一步都会alert数据出来，让你知道出了什么问题
    appId: '',
    timestamp: '', //随便填写一串数字
    nonceStr: '', //随便一字符串
    signature: '', //**这个要到服务器获取**
    jsApiList: [
    'checkJsApi',
    'onMenuShareTimeline',
    'onMenuShareAppMessage',
    'onMenuShareQQ',
    'onMenuShareWeibo',
    'onMenuShareQZone'
    ]
};
function GetRequest() {
  var url = location.search; //获取url中"?"符后的字串
   var theRequest = new Object();
   if (url.indexOf("?") != -1) {
      var str = url.substr(1);
      strs = str.split("&");
      for(var i = 0; i < strs.length; i ++) {
         theRequest[strs[i].split("=")[0]]=(strs[i].split("=")[1]);
      }
   }
   return theRequest;
}
function wxGetSign () {
    var wx_data={};
    wx_data["url"]=(location.href.split('#')[0]);
    var Request = GetRequest();
    wx_id=Request['code'];
    if (wx_id==undefined)
    {
        wx_id="wxc3d3865fb17a924b";
    }
    wx_data["code"]=wx_id;
    //alert(JSON.stringify(wx_data));
    //data1["appid"]= "wxc3d3865fb17a924b";
    // 自己找个ajax库
    url="/weixin/gensign";
    $.ajax({
        type: "POST",
        url: url,
        data: wx_data,
        dataType: "json",
        timeout: 4000,
        async:false,
        success: function(result) {
            if(result["signature"])
            {
                // 获取签名成功，初始化分享
                wxConfigData["signature"]=result["signature"];
                wxConfigData["appId"]=result["appid"];
                wxConfigData["timestamp"]=result["timestamp"];
          　　　 wxConfigData["nonceStr"]=result["nonceStr"];
                wxInit();
            }
        }
    });
}
          // 初始化，已经获得签名
function wxInit ()
{
    wx.config(wxConfigData);
    // 分享
    wx.ready(function(){
        addWeixinShareListening();
    });
    wx.error(function(res){
          var last=JSON.stringify(res);
          //alert(last);
    });
    wx.checkJsApi({
    jsApiList: ['chooseImage'], // 需要检测的JS接口列表，所有JS接口列表见附录2,
    success: function(res) {
         // alert(JSON.stringify(res));
        // 以键值对的形式返回，可用的api值true，不可用为false
        // 如：{"checkResult":{"chooseImage":true},"errMsg":"checkJsApi:ok"}
    }
});
}


         // 分享绑定
function addWeixinShareListening () {
     var host=window.location.host;
     var wx_data={};
     var Request = new Object();
     Request = GetRequest();
     code=Request['code'];
     wx_data['code']=code;
     url="/weixin/code";
     link_url=Request['redirect'];
     //alert(link_url);
     if (link_url==undefined)
     {
        link_url=window.location.href;
     }
    else
     {
         link_url=decodeURIComponent(link_url);
     }
     desc = $("meta[name=description]").attr('content');
     title = $(document).find("title").text();
     img_url = null;
     var images = $('img');
     images.each(function () {
         var that = $(this)[0];
         if (that.width >= 300 && that.height >= 300) {
             img_url = that.src;
             return false;}});
     $.ajax({
        type: "POST",
        url: url,
        data: wx_data,
        dataType: "json",
        timeout: 40000,
        async:false,
        success: function(result) {
            if(result["success"])
            {
                img_url=decodeURI(result['imageurl']);
                title=decodeURI(result['title']);
                desc=decodeURI(result['desc']);
            }
        }
    });
     wxData=
     {
         title : title,
         desc : desc,
         link : link_url,
         imgUrl : img_url,
         type: '',
         dataUrl: '',
    success: function () {
        new_url="/weixin/share";
        $.ajax({
        type: "POST",
        url: new_url,
        data: wx_data,
        dataType: "json",
        timeout: 40000,
        async:false,
        success: function(result) {
            if(result["success"])
            {

            }
        }
    });
        alert('分享成功');
        //分享成功
       //do something!
    }};
    //alert(JSON.stringify(wxData));
    wx.onMenuShareTimeline(wxData);
    wx.onMenuShareAppMessage(wxData);
    wx.onMenuShareQQ(wxData);
    wx.onMenuShareWeibo(wxData);
}