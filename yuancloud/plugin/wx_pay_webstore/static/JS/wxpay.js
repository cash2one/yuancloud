//yuancloud.define('wx_pay_webstore', function (require) {
//    "use strict";
//    var ajax = require('web.ajax');
//    var website = require('website.website');
//    var base = require('web_editor.base');
    $(document).ready(function () {
        var url = document.getElementById("qrcodevalue").value;
        if (url != "") {
            //参数1表示图像大小，取值范围1-10；参数2表示质量，取值范围'L','M','Q','H'
            jQuery('#qrcode').qrcode({
                render: "canvas",
                text: url,
                width: 200, //宽度
                height: 200
            });
        }
        else {
            document.getElementById("box").style.display = "none"
        }
        //setInterval(queryOrderState, 10000);
        var trade_type = $("#trade_type").val();
        if (trade_type == "JSAPI") {

            document.getElementById("pay").style.display = "block";
            document.getElementById("jsPay").style.display = "none";
            wxGetSign();
            waylin();
        }
        else {
            document.getElementById("pay").style.display = "none";
            document.getElementById("jsPay").style.display = "none"
        }
    });

    /*function queryOrderState() {
        order_id = $("#orderid").val();
        $.jsonRpc('/shop/payment/get_status/' + order_id, 'call', {}).then(function (result) {
            if (result.state == 'done') {
                window.location.href = "/shop";
            }
        });
    };*/

    var order_id = $("#orderid").val();
    // 微信分享的数据
    var wxData = {

        title: '',
        desc: '',
        link: "/payment/weixin/directpayment?order_id=" + order_id,
        imgUrl: '',
        type: '',
        dataUrl: '',
        success: function () {
            alert('分享成功');
            //分享成功
            //do something!
        }
    };
    // 配置数据
    var wxConfigData = {
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
            'onMenuShareQZone',
            'chooseWXPay'
        ]
    };
    var wxPayData = {
        appId: "",
        timeStamp: "",
        nonceStr: "",
        package: "",
        signType: "",
        paySign: ""
    };
    // 获取签名
    function wxGetSign() {
        var data1 = {};
        data1["url"] = (location.href.split('#')[0]);
        data1["appid"] = $("#appid").val();
        // 自己找个ajax库
        var url = "/payment/weixin/sign";
        $.ajax({
            type: "POST",
            url: url,
            data: data1,
            dataType: "json",
            timeout: 4000,
            async: false,
            success: function (result) {
                if (result["signature"]) {
                    // 获取签名成功，初始化分享
                    wxConfigData["signature"] = result["signature"];
                    wxConfigData["appId"] = data1["appid"];
                    wxConfigData["timestamp"] = result["timestamp"];
                    wxConfigData["nonceStr"] = result["nonceStr"];
                    wxInit();
                }
            }
        });
    };

    // 初始化，已经获得签名
    function wxInit() {
        wx.config(wxConfigData);
        // 分享
        wx.ready(function () {
            addWeixinShareListening();
        });
        wx.error(function (res) {
            var last = JSON.stringify(res);
            //alert(last);
        });
        wx.checkJsApi({
            jsApiList: ['chooseImage'], // 需要检测的JS接口列表，所有JS接口列表见附录2,
            success: function (res) {
                // alert(JSON.stringify(res));
                // 以键值对的形式返回，可用的api值true，不可用为false
                // 如：{"checkResult":{"chooseImage":true},"errMsg":"checkJsApi:ok"}
            }
        });
    };

    // 分享绑定
    function addWeixinShareListening() {
        var host = window.location.host;
        //var port=window.location.port;
        var appid = $("#appid").val();
        //alert(host);
        var link_url = "http://" + host + "/payment/weixin/otherpayment?order_id=" + order_id + "&appid=" + appid;
        //alert(link_url);
        wxData =
        {
            title: '帮忙代付',
            desc: '江湖救急',
            link: link_url,
            imgUrl: '',
            type: '',
            dataUrl: '',
            success: function () {
                alert('分享成功');
                //分享成功
                //do something!
            }
        };
        //alert(JSON.stringify(wxData));
        wx.onMenuShareTimeline(wxData);
        wx.onMenuShareAppMessage(wxData);
        wx.onMenuShareQQ(wxData);
        wx.onMenuShareWeibo(wxData);
    };

    function waylin() {
        var paydata = {};
        paydata["appid"] = $("#appid").val();
        paydata["package"] = "" + $("#prepay_id").val();
        var payurl = "/payment/weixin/paysign";
        $.ajax({
            type: "POST",
            url: payurl,
            data: paydata,
            dataType: "json",
            timeout: 4000,
            async: false,
            success: function (result) {
                if (result["paySign"]) {
                    // 获取签名成功，初始化分享
                    wxPayData["appId"] = result["appId"];
                    wxPayData["timeStamp"] = result["timeStamp"];
                    wxPayData["nonceStr"] = result["nonceStr"];
                    wxPayData["package"] = result["package"];
                    wxPayData["signType"] = result["signType"];
                    wxPayData["paySign"] = result["paySign"];
                    //alert(JSON.stringify(wxPayData));
                }
            }
        });
    };

    //调用微信JS api 支付
    function jsApiCall() {
        WeixinJSBridge.invoke(
            'getBrandWCPayRequest',
            {
                "appId": wxPayData["appId"],     //公众号名称，由商户传入
                "timeStamp": wxPayData["timeStamp"],         //时间戳，自1970年以来的秒数
                "nonceStr": wxPayData["nonceStr"], //随机串
                "package": wxPayData["package"],
                "signType": wxPayData["signType"],         //微信签名方式：
                "paySign": wxPayData["paySign"] //微信签名
            },
            function (res) {
                 if(res.err_msg == "get_brand_wcpay_request：ok" ) {
                     //alert('');
                 }     // 使用以上方式判断前端返回,微信团队郑重提示：res.err_msg将在用户支付成功后返回    ok，但并不保证它绝对可靠。
                 //alert(res.err_code+res.err_desc+res.err_msg);
            }
        );
    };

    function shareinfoCall() {
        var host = window.location.host;
        //var port=window.location.port;
        var appid = $("#appid").val();
        //alert(host);
        var link_url = "http://" + host + "/payment/weixin/otherpayment?order_id=" + order_id + "&appid=" + appid;
        //alert(link_url);
        wxData =
        {
            title: '帮忙代付',
            desc: '江湖救急',
            link: link_url,
            imgUrl: '',
            type: '',
            dataUrl: '',
        };
        //alert(JSON.stringify(wxData));
        //wx.onMenuShareTimeline(wxData);
        WeixinJSBridge.invoke('shareTimeline', wxData, function (res) {
            WeixinJSBridge.log(res.errMsg);
        });
    };

    function shareinfo() {
        if (typeof WeixinJSBridge == "undefined") {
            if (document.addEventListener) {
                document.addEventListener('WeixinJSBridgeReady', shareinfoCall, false);
            } else if (document.attachEvent) {
                document.attachEvent('WeixinJSBridgeReady', shareinfoCall);
                document.attachEvent('onWeixinJSBridgeReady', shareinfoCall);
            }
        }
        else {
            shareinfoCall();
        }
    };

    function callpay() {
        if (typeof WeixinJSBridge == "undefined") {
            if (document.addEventListener) {
                document.addEventListener('WeixinJSBridgeReady', jsApiCall, false);
            } else if (document.attachEvent) {
                document.attachEvent('WeixinJSBridgeReady', jsApiCall);
                document.attachEvent('onWeixinJSBridgeReady', jsApiCall);
            }
        } else {
            jsApiCall();
        }
    };

    function calljsPay() {
        wx.chooseWXPay({
            timestamp: wxPayData["timeStamp"], // 支付签名时间戳，注意微信jssdk中的所有使用timestamp字段均为小写。但最新版的支付后台生成签名使用的timeStamp字段名需大写其中的S字符
            nonceStr: wxPayData["nonceStr"], // 支付签名随机串，不长于 32 位
            package: wxPayData["package"], // 统一支付接口返回的prepay_id参数值，提交格式如：prepay_id=***）
            signType: wxPayData["signType"], // 签名方式，默认为'SHA1'，使用新版支付需传入'MD5'
            paySign: wxPayData["paySign"], // 支付签名
            success: function (res) {
                // 支付成功后的回调函数
                //alert(JSON.stringify(res));
            }
        });
    };
//});