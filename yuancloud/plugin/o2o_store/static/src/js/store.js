yuancloud.define('o2o_store', function (require) {
    "use strict";
    var core = require('web.core');
    var form_common = require('web.form_common');

    var tencentMapwidget = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
        //instance.web.form.tencentMapwidget = instance.web.form.FormWidget.extend({
        template: 'tencentMap',
        start: function () {
            this.field_manager.on("field_changed:latitude", this, this.load_map);
            this.field_manager.on("field_changed:longitude", this, this.load_map);
            this.load_map();
        },
        load_map: function () {
            var lat = this.field_manager.get_field_value('latitude');
            var lng = this.field_manager.get_field_value('longitude');
            if (lat || lng) {
                var params = {
                    center: lng + ',' + lat,
                    'size': '360*180',
                    'markers': lng + ',' + lat,
                    'zoom': 15,
                };
                var map_url = 'http://st.map.qq.com/api?' + $.param(params);
                this.$el.find('img').attr('src', map_url);

                var addr = this.field_manager.get_field_value('address') || "";
                var title = this.field_manager.get_field_value('name') || "";
                params = {
                    marker: 'coord:' + lat + ',' + lng + ';title:' + title + ';addr:' + addr,
                }
                var map_link = 'http://apis.map.qq.com/uri/v1/marker?' + $.param(params);
                this.$el.attr('href', map_link);
            }
        },
    });
    //core.form_custom_registry.add('tencentMap', 'instance.web.form.tencentMapwidget');

    core.form_custom_registry.add('tencentMap', tencentMapwidget);
});