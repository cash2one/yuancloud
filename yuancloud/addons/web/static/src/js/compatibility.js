// ------------------------------------------------------------------------------
// Compatibility with YuanCloud v8.  
// 
// With the new module system, no global variable can (and should) be accessed
// in yuancloud.  This file exports everything, to mimic the previous global 
// namespace structure.  This is only supposed to be used by 3rd parties to 
// facilitate migration.  YuanCloud addons should not use the 'yuancloud' variable at 
// all.
// ------------------------------------------------------------------------------
yuancloud.define('web.compatibility', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var FavoriteMenu = require('web.FavoriteMenu');
var form_common = require('web.form_common');
var formats = require('web.formats');
var FormView = require('web.FormView');
var form_relational = require('web.form_relational'); // necessary
var form_widgets = require('web.form_widgets'); // necessary
var framework = require('web.framework');
var ListView = require('web.ListView');
var Menu = require('web.Menu');
var Model = require('web.DataModel');
var pyeval = require('web.pyeval');
var Registry = require('web.Registry');
var SearchView = require('web.SearchView');
var session = require('web.session');
var Sidebar = require('web.Sidebar');
var SystrayMenu = require('web.SystrayMenu');
var time = require('web.time');
var UserMenu = require('web.UserMenu');
var utils = require('web.utils');
var View = require('web.View');
var ViewManager = require('web.ViewManager');
var WebClient = require('web.WebClient');
var Widget = require('web.Widget');

var client_started = $.Deferred();

var OldRegistry = Registry.extend({
    add: function (key, path) {
    },
    get_object: function (key) {
        return get_object(this.map[key]);
    },
});

window.yuancloud = window.yuancloud || {};

$.Mutex = utils.Mutex;
yuancloud._session_id = "instance0";
yuancloud._t = core._t;
yuancloud.get_cookie = utils.get_cookie;

yuancloud.qweb = core.qweb;
yuancloud.session = session;

yuancloud.web = yuancloud.web || {};
yuancloud.web._t = core._t;
yuancloud.web._lt = core._lt;

yuancloud.web.ActionManager = ActionManager;
yuancloud.web.auto_str_to_date = time.auto_str_to_date;
yuancloud.web.blockUI = framework.blockUI;
yuancloud.web.BufferedDataSet = data.BufferedDataSet;
yuancloud.web.bus = core.bus;
yuancloud.web.Class = core.Class;
yuancloud.web.client_actions = make_old_registry(core.action_registry);
yuancloud.web.CompoundContext = data.CompoundContext;
yuancloud.web.CompoundDomain = data.CompoundDomain;
yuancloud.web.DataSetSearch = data.DataSetSearch;
yuancloud.web.DataSet = data.DataSet;
yuancloud.web.date_to_str = time.date_to_str;
yuancloud.web.Dialog = Dialog;
yuancloud.web.DropMisordered = utils.DropMisordered;

yuancloud.web.form = yuancloud.web.form || {};
yuancloud.web.form.AbstractField = form_common.AbstractField;
yuancloud.web.form.compute_domain = data.compute_domain;
yuancloud.web.form.DefaultFieldManager = form_common.DefaultFieldManager;
yuancloud.web.form.FieldChar = core.form_widget_registry.get('char');
yuancloud.web.form.FieldFloat = core.form_widget_registry.get('float');
yuancloud.web.form.FieldStatus = core.form_widget_registry.get('statusbar');
yuancloud.web.form.FieldMany2ManyTags = core.form_widget_registry.get('many2many_tags');
yuancloud.web.form.FieldMany2One = core.form_widget_registry.get('many2one');
yuancloud.web.form.FormWidget = form_common.FormWidget;
yuancloud.web.form.tags = make_old_registry(core.form_tag_registry);
yuancloud.web.form.widgets = make_old_registry(core.form_widget_registry);

yuancloud.web.format_value = formats.format_value;
yuancloud.web.FormView = FormView;

yuancloud.web.json_node_to_xml = utils.json_node_to_xml;

yuancloud.web.ListView = ListView;
yuancloud.web.Menu = Menu;
yuancloud.web.Model = Model;
yuancloud.web.normalize_format = time.strftime_to_moment_format;
yuancloud.web.py_eval = pyeval.py_eval;
yuancloud.web.pyeval = pyeval;
yuancloud.web.qweb = core.qweb;

yuancloud.web.Registry = OldRegistry;

yuancloud.web.search = {};
yuancloud.web.search.FavoriteMenu = FavoriteMenu;
yuancloud.web.SearchView = SearchView;
yuancloud.web.Sidebar = Sidebar;
yuancloud.web.str_to_date = time.str_to_date;
yuancloud.web.str_to_datetime = time.str_to_datetime;
yuancloud.web.SystrayItems = SystrayMenu.Items;
yuancloud.web.unblockUI = framework.unblockUI;
yuancloud.web.UserMenu = UserMenu;
yuancloud.web.View = View;
yuancloud.web.ViewManager = ViewManager;
yuancloud.web.views = make_old_registry(core.view_registry);
yuancloud.web.WebClient = WebClient;
yuancloud.web.Widget = Widget;

yuancloud.Widget = yuancloud.web.Widget;
yuancloud.Widget.prototype.session = session;


WebClient.include({
    init: function () {
        yuancloud.client = this;
        yuancloud.webclient = this;
        start_modules();
        client_started.resolve();
        this._super.apply(this, arguments);
    },
});


function make_old_registry(registry) {
    return {
        add: function (key, path) {
            client_started.done(function () {
                registry.add(key, get_object(path));
            });
        },
    };
}
function get_object(path) {
    var object_match = yuancloud;
    path = path.split('.');
    // ignore first section
    for(var i=1; i<path.length; ++i) {
        object_match = object_match[path[i]];
    }
    return object_match;
}

/**
 * YuanCloud instance constructor
 *
 * @param {Array|String} modules list of modules to initialize
 */
var inited = false;
function start_modules (modules) {
    if (modules === undefined) {
        modules = yuancloud._modules;
    }
    modules = _.without(modules, "web");
    if (inited) {
        throw new Error("YuanCloud was already inited");
    }
    inited = true;
    for(var i=0; i < modules.length; i++) {
        var fct = yuancloud[modules[i]];
        if (typeof(fct) === "function") {
            yuancloud[modules[i]] = {};
            for (var k in fct) {
                yuancloud[modules[i]][k] = fct[k];
            }
            fct(yuancloud, yuancloud[modules[i]]);
        }
    }
    yuancloud._modules = ['web'].concat(modules);
    return yuancloud;
};

// Monkey-patching of the ListView for backward compatibiliy of the colors and
// fonts row's attributes, as they are deprecated in 9.0.
ListView.include({
    view_loading: function(fvg) {
        this._super(fvg);

        if (this.fields_view.arch.attrs.colors) {
            this.colors = _(this.fields_view.arch.attrs.colors.split(';')).chain()
                .compact()
                .map(function(color_pair) {
                    var pair = color_pair.split(':'),
                        color = pair[0],
                        expr = pair[1];
                    return [color, py.parse(py.tokenize(expr)), expr];
                }).value();
        }

        if (this.fields_view.arch.attrs.fonts) {
            this.fonts = _(this.fields_view.arch.attrs.fonts.split(';')).chain().compact()
                .map(function(font_pair) {
                    var pair = font_pair.split(':'),
                        font = pair[0],
                        expr = pair[1];
                    return [font, py.parse(py.tokenize(expr)), expr];
                }).value();
        }
    },
    /**
     * Returns the style for the provided record in the current view (from the
     * ``@colors`` and ``@fonts`` attributes)
     *
     * @param {Record} record record for the current row
     * @returns {String} CSS style declaration
     */
    style_for: function (record) {
        var len, style= '';

        var context = _.extend({}, record.attributes, {
            uid: session.uid,
            current_date: moment().format('YYYY-MM-DD')
            // TODO: time, datetime, relativedelta
        });
        var i;
        var pair;
        var expression;
        if (this.fonts) {
            for(i=0, len=this.fonts.length; i<len; ++i) {
                pair = this.fonts[i];
                var font = pair[0];
                expression = pair[1];
                if (py.PY_isTrue(py.evaluate(expression, context))) {
                    switch(font) {
                    case 'bold':
                        style += 'font-weight: bold;';
                        break;
                    case 'italic':
                        style += 'font-style: italic;';
                        break;
                    case 'underline':
                        style += 'text-decoration: underline;';
                        break;
                    }
                }
            }
        }
 
        if (!this.colors) { return style; }
        for(i=0, len=this.colors.length; i<len; ++i) {
            pair = this.colors[i];
            var color = pair[0];
            expression = pair[1];
            if (py.PY_isTrue(py.evaluate(expression, context))) {
                return style += 'color: ' + color + ';';
            }
        }
        return style;
     },
});


});
