(function(HSH) {

var $body = $('body');
HSH.env = {};

HSH.networkType = 'unknown';

HSH.shareTimelineData = {
  title:'',
  link:'',
  imgUrl:'',
  success:function(){}
};

HSH.shareAppData = {
  title: '', // 分享标题
  desc: '', // 分享描述
  link: '', // 分享链接
  imgUrl: '', // 分享图标
  success:function(){}
};

HSH.shareQQ = {
  title: '', // 分享标题
  desc: '', // 分享描述
  link: '', // 分享链接
  imgUrl: '', // 分享图标
  success:function(){}
};

HSH.shareWeibo = {
   title: '', // 分享标题
    desc: '', // 分享描述
    link: '', // 分享链接
    imgUrl: '', // 分享图标
  success:function(){}
};

HSH.shareQZone = {
 title: '', // 分享标题
    desc: '', // 分享描述
    link: '', // 分享链接
    imgUrl: '', // 分享图标
  success:function(){}
};

HSH.jsApiList = [];

HSH.hideMenuList = [];

HSH.wxconfig = function(config, debug, callback) {
  //alert(debug);
  config = JSON.parse(config);
  config.debug = debug;
  config.jsApiList = HSH.jsApiList;
  var last=JSON.stringify(config);
  //alert(last);
  wx.config(config);
  wx.error(function(res){
          var last=JSON.stringify(res);
          //alert(last);
    });
  wx.ready(function() {
    wx.onMenuShareTimeline(HSH.shareTimelineData);
    wx.onMenuShareAppMessage(HSH.shareAppData);
    wx.onMenuShareQQ(HSH.shareQQ);
    wx.onMenuShareWeibo(HSH.shareWeibo);
    wx.onMenuShareQZone(HSH.shareQZone);
    setInterval((function getNetworkType() {
      wx.getNetworkType({
        success: function (res) {
          HSH.networkType = res.networkType;
        }
      });
      return getNetworkType;
    })(), 2000);

    if (typeof callback === 'function') {
      callback();
    }
  });
};

HSH.alert = function(message) {
  var $alert = $('#lh-alert');

  if (!$alert.length) {
    $alert = $('<div id="lh-alert" class="alert"><p></p></div>');
    $alert.hide();
    $alert.on('tap', function() {
      $alert.hide();
    });
    $body.append($alert);
  }

  clearTimeout($alert.data('timer'));

  $alert.find('p').text(message);
  $alert.show();

  $alert.data('timer', setTimeout(function() {
    $alert.animate({
      opacity: 0
    }, 300, 'ease-out', function() {
      $alert.css({opacity: '1', display: 'none'});
    });
  }, 1500));
};

HSH.cookies = function() {
  return document.cookie.split(/;\s*/).reduce(function(result, str) {
    var parts = str.split('=');
    result[parts[0]] = parts[1];
    return result;
  }, {});
};

HSH.ajax = function(options) {
  if (!options) {
    options = {};
  }

  options.headers = options.headers || {};
  options.headers['X-Network-Type'] = HSH.networkType;

  return $.ajax(options);
};

window.HSH = HSH;
window.LH = HSH;

})(window.HSH || {});
