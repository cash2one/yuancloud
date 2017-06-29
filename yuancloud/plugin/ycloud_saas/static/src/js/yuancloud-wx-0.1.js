/**
 * Created by sswy on 12/7/15.
 */
var weixin_option = {
    debug: false,
    appid: '',
    hideOptionMenu: false,
    timestamp: '',
    nonceStr: '',
    signature: '',
    jsApiList: [
        'checkJsApi',
        'onMenuShareTimeline',
        'onMenuShareAppMessage',
        'onMenuShareQQ',
        'onMenuShareWeibo',
        'getLocation'] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
};

//$(document).ready(function () {
//    $('#check').click(function (event) {
//        data = $('form').serialize();
//        window.location.href = '/mobile/ui/profile?' + data;
//    });
//
//    $('#back').click(function (event) {
//        //wx.closeWindow();
//        history.back();
//    });
//
//    $("#sendgeo").click(function (event) {
//        getlocation();
//        //event.preventDefault();
//        //$('#dialog').show();
//        //$('#dialog').find('.weui_btn_dialog').on('click', function () {
//        //    $('#dialog').hide();
//        //});
//        return false;
//    });
//
//
//    //weixin api
//    /*
//
//     //$('.linkab').on('click', function (ev) {
//     //var b = $(event.target).attr('newurl');
//     //window.location.href='/mobile/sample/'+b;
//     });
//     */
//});


//function getlocation() {
//    $('.ui-loading-wrap').show();
//    wx.getLocation({
//        type: 'wgs84', // 默认为wgs84的gps坐标，如果要返回直接给openLocation用的火星坐标，可传入'gcj02'
//        success: function (res) {
//            var latitude = res.latitude; // 纬度，浮点数，范围为90 ~ -90
//            var longitude = res.longitude; // 经度，浮点数，范围为180 ~ -180。
//            var speed = res.speed; // 速度，以米/每秒计
//            var accuracy = res.accuracy; // 位置精度
//
//            $("#latitude").val(latitude);
//            $("#longitude").val(longitude);
//
//            var geocoder = new qq.maps.Geocoder({
//                complete: function (result) {
//                    $("#getinfo").val(result.detail.address);
//                    $('.ui-loading-wrap').hide();
//                }
//            });
//            var coord = new qq.maps.LatLng(latitude, longitude);
//            qq.maps.convertor.translate(coord, 1, function (res) {
//                geocoder.getAddress(new qq.maps.LatLng(res[0]["lat"], res[0]["lng"]));
//            });
//        }
//    });
//}

$.post('/wx/app/getwechatapidata', {url: window.location.href}, function (data) {
    wx.config({
        debug: weixin_option.debug, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
        appId: data.appid, // 必填，公众号的唯一标识
        timestamp: data.timestamp, // 必填，生成签名的时间戳
        nonceStr: data.nonceStr, // 必填，生成签名的随机串
        signature: data.signature,// 必填，签名，见附录1
        jsApiList: weixin_option.jsApiList
    });

    wx.ready(function () {
        //getlocation();
        img_url = null;
        var images = $('img');
        images.each(function () {
            var that = $(this)[0];
            if (that.width >= 300 && that.height >= 300) {
                img_url = that.src;
                return false;
            }
        })
        wx.onMenuShareAppMessage({
            title: $(document).find("title").text(), // 分享标题
            desc: $("meta[name=description]").attr('content'),//'日暮苍山远，天寒白屋贫。柴门闻犬吠，风雪夜归人。', // 分享描述
            link: window.location.href, // 分享链接
            imgUrl: img_url, // 分享图标
            type: '', // 分享类型,music、video或link，不填默认为link
            dataUrl: '', // 如果type是music或video，则要提供数据链接，默认为空
            success: function () {
                // 用户确认分享后执行的回调函数
            },
            cancel: function () {
                // 用户取消分享后执行的回调函数
            }
        });
    });

    wx.error(function (res) {

    });
}, 'json');

