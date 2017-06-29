yuancloud.define('website_sale.wxpay_validate', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    $(document).ready(function () {
        function payment_transaction_poll_status() {
            order_id = $("#orderid").val();
            ajax.jsonRpc('/shop/get_status/' + order_id, 'call', {}).then(function (result) {
                if (result.state == 'done') {
                    window.location.href = "/shop";
                }
            });
            setTimeout(function () {
                payment_transaction_poll_status();
            }, 1000);
        }
        payment_transaction_poll_status();
    });
});
