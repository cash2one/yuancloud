yuancloud.web_extended = function (instance, local) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;
    //instance.web.ListView.include({
    //    load_list: function () {
    //        //if (!this.$buttons) {
    //        //    this.$buttons = $(QWeb.render("ListView.buttons", {'widget': self}));
    //        //    if (this.options.$buttons) {
    //        //        this.$buttons.appendTo(this.options.$buttons);
    //        //    } else {
    //        //        this.$el.find('.oe_list_buttons').replaceWith(this.$buttons);
    //        //    }
    //        //    this.$buttons.find('.oe_list_add')
    //        //        .click(this.proxy('do_add_record'))
    //        //        .prop('disabled', this.grouped);
    //        //}
    //    }
    //});

    instance.web.form.widgets.add('web_extended.geo', 'yuancloud.web.form.ycloud_web_geo');


    yuancloud.web.form.ycloud_web_geo = instance.web.form.FieldChar.extend(
        {
            template: 'web_extended.geo',

            start: function () {
                var self = this;
                this._super();
                //debugger;
                var oldsrc = this.$el.find('iframe').attr('src');

                var lat = this.field_manager.get_field_value("geo_latitude");
                var lng = this.field_manager.get_field_value("geo_longitude");

                var field_addr = this.getParent().fields['addr'];
                var field_latitude = this.getParent().fields['geo_latitude'];
                var field_longitude = this.getParent().fields['geo_longitude'];
                if (lat > 0 || lng > 0) {
                    this.$el.find('iframe').attr('src', oldsrc + '&coord=' + lat + ',' + lng);
                }
                window.addEventListener('message', function (event) {
                    // 接收位置信息，用户选择确认位置点后选点组件会触发该事件，回传用户的位置信息
                    var loc = event.data;
                    //$("#company_geo").find("input")[0].value = loc.latlng.lat;
                    //$("#company_geo").find("input")[1].value = loc.latlng.lng;
                    field_latitude.set_value(loc.latlng.lat);
                    field_longitude.set_value(loc.latlng.lng);
                    field_addr.set_value(loc.poiaddress + loc.poiname);

                }, false);
            },
        });
};
