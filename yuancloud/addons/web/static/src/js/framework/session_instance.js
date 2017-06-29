yuancloud.define('web.session', function (require) {
    var Session = require('web.Session');
    var modules = yuancloud._modules;
    return new Session(undefined, undefined, {modules:modules, use_cors: false});
});
