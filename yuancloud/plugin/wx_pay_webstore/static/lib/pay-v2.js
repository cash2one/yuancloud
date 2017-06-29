HSH.run = function (t) {
    function o(t)
    {
        L.text.text(t)
    }

    function n(t)
    {
        W.text.text(t), W.input.val(t)
    }

    function e(t, o, n) {
        n || (n = A.name.data("default")), A.text.text(o), A.input.val(o), A.id.val(t), A.name.html(n)
    }

    function a() {
        return k.val()
    }

    function r(t) {
        D.text.text(t), D.input.val(t)
    }

    function i() {
        O.prop("disabled", !1).removeClass("disabled")
    }

    function u() {
        O.prop("disabled", !0).addClass("disabled")
    }

    function c(t) {
        if (t.errorCode > 0)return u(), HSH.alert("对不起，" + t.errorMessage);
        var o = t.data;
        d(o)
    }

    function d(t) {
        k._data = t;
        var a = Math.round(100 * k.val());
        a === t.amount && (t.firstOff && n(t.firstOff), t.couponOff && e(t.couponId, t.couponOff, t.coupon_name), t.activityOff && o(t.activityOff), r(t.realAmount), i())
    }

    function p(t) {
        /*
        "chooseWXPay:cancel" !== t.errMsg && HSH.alert(t.errMsg), LH.ajax({
            url: "/pay/order/cancel/" + g + "?appid=" + M,
            type: "POST",
            success: function (t) {
                return j = !1, g = t.data.orderno, $("#orderno").val(g), i()
            },
            error: function (t, o, n) {
                return Bugsnag.notify("CancelOrderError", n), j = !1, i()
            }
        })*/
    }

    function f(t) {
        "chooseWXPay:ok" == t.errMsg && (H ? setTimeout(function () {
            document.location.href = "/pay/complate/" + g + "?appid=" + M
        }, 1) : $.get("/lottery/count", {orderno: g, appid: M}).done(function (t) {
            return 0 === t.errorCode && t.data > 0 ? void(window.location.href = "/lottery?orderno=" + g + "&appid=" + M) : wx.closeWindow()
        }).fail(function () {
            return wx.closeWindow()
        }))
        /*"chooseWXPay:ok" == t.errMsg && (H ? setTimeout(function () {
            document.location.href = "/pay/code/" + g + "?appid=" + M
        }, 1) : $.get("/lottery/count", {orderno: g, appid: M}).done(function (t) {
            return 0 === t.errorCode && t.data > 0 ? void(window.location.href = "/lottery?orderno=" + g + "&appid=" + M) : wx.closeWindow()
        }).fail(function () {
            return wx.closeWindow()
        }))*/
    }

    function s(t) {
        if (t.errorCode > 0)return i(), j = !1, HSH.alert("对不起，" + t.errorMessage);
        var o = t.data;
        o = JSON.parse(o);
        wx.chooseWXPay({
            timestamp: o.timeStamp,
            nonceStr: o.nonceStr,
            package: o["package"],
            signType: o.signType,
            paySign: o.paySign,
            success: f,
            fail: p,
            cancel: p
        })
    }

    function l() {
        var t = "0.00";
        n(t), e(0, t), o(t), r(t)
    }

    function m() {
        l(), k._oldValue = null, u()
    }

    function v() {
        T.addClass("keyboard-open"), P.text("消费金额")
    }

    function y() {
        T.removeClass("keyboard-open"), C.text().length || P.text("咨询服务员后输入消费金额")
    }

    HSH.options = t;
    var g = t.orderNo, h = t.meid, x = t.maxAmount, H = t.paycodeEnabled || !1, S = t.hasActivity || !1, w = t.activityType || null, b = $("body"), O = $("#submit"), T = $("#pay_form"), k = $("#amount"), C = $("#unit_holder .amount"), P = $("#payholder"), j = !1, M = $('meta[name="lehui-appid"]').attr("content");
    HSH.jsApiList = ["chooseWXPay","onMenuShareAppMessage", "onMenuShareTimeline","closeWindow","onMenuShareQQ","onMenuShareWeibo","onMenuShareQZone","chooseCard","addCard"], HSH.wxconfig(t.signature, !1), b.height($(window).height());
    var W = {text: $("#first_off_text"), input: $("#first_off")}, A = {
        text: $("#coupon_off_text"),
        input: $("#coupon_off"),
        id: $("#coupon_id"),
        name: $("#coupon_name")
    }, D = {
        text: $("#real_amount_text"),
        input: $("#real_amount")
    }, L = {text: $("#activity_off_text")}, X = S === !0 ? 0 : 300;
    dalayTime = "lh_coupon_link" === w ? 300 : X;
    var E = _.debounce(function () {
        var t = a();
        return t.length ? (t = parseFloat(t)) ? k._prevReal === t ? void(k._data && d(k._data)) : (k._prevReal = t, S === !0 && "lh_coupon_link" !== w ? void d({
            couponOff: 0,
            firstOff: 0,
            amount: Math.round(100 * t),
            realAmount: Math.round(100 * t),
            activityOff: 0
        }) : void LH.ajax({
            url: "/pay/amount?appid=" + M,
            type: "POST",
            dataType: "json",
            data: "meid=" + h + "&amount=" + t,
            success: c
        })) : (l(), void u()) : m()
    }, X);
    $("#amount-row").on("tap", function (t) {
        t.preventDefault(), t.stopPropagation(), k.trigger("focus")
    }), O.on("click", function () {
        O.hasClass("disabled") || j || (u(), j = !0, LH.ajax({
            url: "/pay/order?appid=" + M+"&orderNo="+g,
            type: "POST",
            data: T.serialize(),
            dataType: "json",
            success: s,
            error: function (t, o, n) {
                HSH.alert("网络开小差了，请稍后重试"), Bugsnag.notify("PayOrderError", n), j = !1, i()
            }
        }))
    }), b.on("tap", function (t) {
        "amount" !== $(t.target).attr("id") && setTimeout(function () {
            k.trigger("blur")
        }, 0)
    });
    var F = function () {
        var t = 0, o = [], n = !1, e = 0;
        return function (a) {
            if ("backspace" === a) {
                var r = o.pop();
                "." === r ? n = !1 : n && e--
            } else"." === a ? n || (n = !0, o.length || o.push(0), o.push(a)) : (a = parseInt(a), 1 == o.length && 0 === o[0] && o.pop(), n ? 2 > e && (e++, o.push(a)) : o.push(a));
            t = o.join("");
            var i = parseFloat(t);
            return (0 === x && i > 99999 || x > 0 && i >= x) && (HSH.alert("超过可支付最大金额"), o.pop(), t = o.join("")), t
        }
    }();
    $(".key[data-code]").on("touchstart", function (t) {
        t.preventDefault();
        var o = $(t.currentTarget), n = o.data("code"), e = F(n);
        o.addClass("down"), setTimeout(function () {
            o.removeClass("down")
        }, 100), C.text(e), k.val(e), parseFloat(e.length) ? E() : (l(), u())
    }), $("#keyboard-down").on("touchstart", function (t) {
        t.preventDefault(), y()
    }), $("#amount-input").click(function (t) {
        t.preventDefault(), v()
    }), setTimeout(function () {
        v(), t.updateRealAmount && E()
    }, 200)
};