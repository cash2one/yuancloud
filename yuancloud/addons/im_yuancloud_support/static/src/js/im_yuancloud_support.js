yuancloud.define('im_yuancloud_support.yuancloudSupport', function (require) {
"use strict";

var core = require('web.core');
var UserMenu = require('web.UserMenu');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');

var _t = core._t;


var COOKIE_NAME = 'yuancloud_livechat_conversation';
var SERVICE_URL = 'https://services.yuancloud.cn/';

var yuancloudSupport = Widget.extend({
    init: function(login, uuid, params, options){
        this._super();
        this.login = login;
        this.uuid = uuid;

        this.options = _.extend(options || {}, {'defaultUsername' : login});
        this.params = _.extend(params || {}, {'database_uuid' : uuid});

        this.assets_loaded = false;
        this.session = false;
        // bind event
        $(window).on("yuancloud_support_ready_to_bind", this, _.bind(this.bind_actions, this));
    },
    bind_actions: function(event, button){
        if (button === 'usermenu'){
            $('.oe_user_menu_placeholder .yuancloud_support_contact').on('click', this, _.bind(this.click_action, this));
            // check auto start if cookie
            var cookie = utils.get_cookie(COOKIE_NAME);
            if (cookie){
                this.start_support();
            }
        }
        if(button === 'im_contact'){
            if (web_client.im_messaging) {
                web_client.im_messaging.$('.yuancloud_support_contact').on('click',this, _.bind(this.click_action, this));
            }
        }
    },
    click_action: function(){
        var session = utils.get_cookie(COOKIE_NAME);
        if(!session){
            this.start_support();
        }
    },
    start_support: function(){
        var self = this;
        if(!this.assets_loaded){
            this.load_assets().then(function(){
                try{

                    this.support = new yuancloud.LiveSupport(self.options, self.params);
                    // bind event change status
                    this.support.on('im_yuancloud_support_status', this, function(is_online){
                        if(web_client.im_messaging){
                            web_client.im_messaging.support_user.$(".oe_im_user_online").toggle(is_online);
                        }
                    });
                }catch(e){
                    self.error_on_start(e);
                }
            }).fail(function(e){
               self.error_on_start(e);
            });
        }else{
            this.support.start();
        }
    },
    error_on_start: function(e){
        this.assets_loaded = false;
        this.do_warn(_t("Error"), _t("The connection with the YuanCloud Support Server failed. Please retry in a few minutes, or send an email to support@yuancloud.cool ."));
    },
    load_assets: function(){
        var self = this;
        var add_asset = function(file_url, type) {
            var def = $.Deferred();
            if(type === 'js'){
                $.getScript( file_url, function( data, textStatus, jqxhr ) {
                    def.resolve();
                }).fail(function(){
                    def.reject();
                });
                return def;
            }else{
                $('<link rel="stylesheet" href="' + file_url + '"></link>').appendTo($("head")).ready(function() {
                    def.resolve();
                });
                return def;
            }
        };
        var defs = [];
        defs.push(add_asset(SERVICE_URL+"yuancloud-livechat/assets/js", 'js'));
        defs.push(add_asset(SERVICE_URL+"yuancloud-livechat/assets/css", 'css'));
        return $.when.apply($, defs).then(function(res){
            self.assets_loaded = true;
            return res;
        }, function(){
            self.error_on_start();
        });
    },
});

UserMenu.include({
    do_update: function(){
        $(window).trigger('yuancloud_support_ready_to_bind', 'usermenu');
        return this._super.apply(this, arguments);
    },
});

return yuancloudSupport;

});

