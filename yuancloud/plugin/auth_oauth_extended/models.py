# -*- coding: utf-8 -*-

from werkzeug.exceptions import BadRequest
import functools
import logging
import simplejson
import urllib2
import urlparse
import collections
import urlparse
import werkzeug.urls
import werkzeug.utils
import yuancloud
from yuancloud import cache
from yuancloud import models, fields
from yuancloud import http
from yuancloud import SUPERUSER_ID
from yuancloud.osv import osv
from yuancloud.addons.auth_oauth.controllers.main import fragment_to_query_string
from yuancloud.addons.auth_oauth.controllers.main import OAuthController
from yuancloud.addons.auth_signup.controllers.main import AuthSignupHome as Home
from yuancloud.addons.auth_signup.res_users import SignupError
from yuancloud.addons.web.controllers.main import db_monodb
from yuancloud.addons.web.controllers.main import ensure_db
from yuancloud.addons.web.controllers.main import login_and_redirect
from yuancloud.addons.web.controllers.main import set_cookie_and_redirect
from yuancloud.http import request
from yuancloud.modules.registry import RegistryManager
import base64
import re

from yuancloud.tools.translate import _

_logger = logging.getLogger(__name__)


def is_json(data):
    try:
        simplejson.loads(data)
    except ValueError, e:
        return False
    return True


class OAuthController_extend(OAuthController):
    def query_user_login(self, cr, registry, login_id, context):
        oauth_provider = registry.get('oauth_provider_entity_extend')
        oauth_provider_id = oauth_provider.search(cr, SUPERUSER_ID, [('oauth_uid', '=', login_id)], context)
        if oauth_provider_id:
            oauth_provider_info = oauth_provider.browse(cr, SUPERUSER_ID, oauth_provider_id, context)
            return oauth_provider_info['res_user_id'].id
        else:
            return False

    @http.route('/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        # saas auth goto super
        if is_json(kw['state']):
            return super(OAuthController_extend, self).signin(**kw)
        # kw = simplejson.loads(simplejson.dumps(kw).replace('+',''))
        state = simplejson.loads((kw['state'] + "==").decode('base64'))
        dbname = state.get('d', 'yuancloud')
        provider = state.get('p', 5)
        context = state.get('c', {})
        code = kw.get('code', "")
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            try:
                u = registry.get('res.users')
                # provider_obj = registry.get('auth.oauth.provider').read(cr, SUPERUSER_ID, provider, context=context)
                # if provider_obj['provider_type'] == "weixin":
                #     appid = "wx308ff9aef6d394a9"
                #     appsecret = "16bb5929155d1edb5f82ee6311f04158"
                #     access_token = self.get_access_token(appid, appsecret, code)
                kw.update({"access_token": code})
                user_login_info = u.get_user_login_info(cr, SUPERUSER_ID, provider, kw, context=context)
                login_id = user_login_info['validation'][user_login_info['oauth_uid']]
                print login_id
                user_id = self.query_user_login(cr, registry, login_id, context)
                # user_id = u.search(cr, SUPERUSER_ID,
                #                    [("oauth_uid", "=", login_id), '|', ('active', '=', True), ('active', '=', False)])
                if user_id:
                    user = u.browse(cr, SUPERUSER_ID, user_id, context)
                    if user.active:
                        # {"validation":validation,"oauth_uid":oauth_uid,"params":params}
                        params = user_login_info['params']
                        validation = user_login_info['validation']
                        access_token = user_login_info['access_token']
                        params.update({'validation': validation, 'access_token': access_token})

                        credentials = u.auth_oauth(cr, SUPERUSER_ID, provider, params, context=context)
                        cr.commit()
                        action = state.get('a')
                        menu = state.get('m')
                        redirect = werkzeug.url_unquote_plus(state['r']) if state.get('r') else False
                        url = '/web'
                        if redirect:
                            url = redirect
                        elif action:
                            url = '/web#action=%s' % action
                        elif menu:
                            url = '/web#menu_id=%s' % menu
                        return login_and_redirect(*credentials, redirect_url=url)
                    else:
                        _logger.error('active is false')
                        raise 'active is false'
                else:  # 用户不存在时，需要跳转到注册页面，或者绑定现有帐号;
                    name = login_id
                    access_token = user_login_info['access_token']
                    if 'nickname' in user_login_info['validation']:
                        name = user_login_info['validation']['nickname']
                    if 'name' in user_login_info['validation']:
                        name = user_login_info['validation']['name']
                    openid = login_id
                    url = werkzeug.url_unquote_plus(
                        '/web/signup/?name={0}&oauth_uid={1}&oauth_provider_id={2}&reset=false&oauth_access_token={3}'.format(
                            name, openid, provider, access_token))
                    return set_cookie_and_redirect(url)
                    # pass
                    # credentials = u.auth_oauth(cr, SUPERUSER_ID, provider, user_login_info['params'],user_login_info['validation'],user_login_info['access_token'], context=context)
                    # cr.commit()
                    # action = state.get('a')
                    # menu = state.get('m')
                    # redirect = werkzeug.url_unquote_plus(state['r']) if state.get('r') else False
                    # url = '/web'
                    # if redirect:
                    #     url = redirect
                    # elif action:
                    #     url = '/web#action=%s' % action
                    # elif menu:
                    #     url = '/web#menu_id=%s' % menu
                    # return login_and_redirect(*credentials, redirect_url=url)
            except AttributeError:
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: oauth sign up cancelled." % (dbname,))
                url = "/web/login?oauth_error=1"
            except yuancloud.exceptions.AccessDenied:
                # oauth credentials not valid, user could be on a temporary session
                _logger.info(
                    'OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/web/login?oauth_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception, e:
                # signup error
                _logger.exception("OAuth2: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return set_cookie_and_redirect(url)


class auth_oauth_provider(models.Model):
    _inherit = 'auth.oauth.provider'

    provider_type = [
        ('qq', 'for QQ'),
        ('pc_weixin', 'for Openplatform'),
        ('weixin', 'for Weixin'),
        ('weixin_qy', 'for Weixin_qy'),
        ('weibo', 'for Weibo'),
        ('other', 'for Other'),
    ]
    provider_type = fields.Selection(provider_type, 'Provider Type', required=True)
    provider_browser = fields.Selection([('pc', '网页浏览器'), ('weixin', '微信浏览器'), ('mobile', '手机浏览器')], '支持浏览器')
    client_sercret = fields.Char("Client Sercret")
    _defaults = {
        'provider_type': 'other',
    }


class res_users(osv.Model):
    _inherit = 'res.users'

    def get_access_token(self, url, appid, appsecret, code):
        url = url + "?appid=" + appid + "&secret=" + appsecret + "&code=" + code + "&grant_type=authorization_code"
        f = urllib2.urlopen(url)
        response = f.read()
        result = simplejson.loads(response)
        if 'errcode' in result:
            return {"error": "无效的code!"}
        else:
            return result

    def get_qy_access_token(self, url, appid, appsecret, code):
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (appid, appsecret)
        # return url;
        key = appid + '_access_token'
        # mc = getClient()
        token = cache.redis.get(key)
        if token == None:
            response = urllib2.urlopen(access_token_url)
            html = response.read().decode("utf-8")
            tokeninfo = simplejson.loads(html)
            if "errcode" in tokeninfo:
                return {'error': "获取AccessToken出错" + str(tokeninfo['errcode']) + tokeninfo['errmsg']}
            else:
                token = tokeninfo['access_token']
                logging.debug("token:" + token)
                cache.redis.set(key, token, 7200)
                # mc.set(key, token, 7200)
        token = cache.redis.get(key)
        logging.debug("getAccessToken:" + token)
        result = self.getuserinfo(url, code, token)
        real_result = {}
        if 'OpenId' in result:
            real_result.update({
                "UserId": result['OpenId']
            })
        elif 'UserId' in result:
            real_result.update({
                'UserId': result['UserId']
            })
        real_result.update({
            "access_token": token
        })
        return real_result

    def getuserdetailinfo(self, url, access_token, openid):
        url = url + "?access_token=" + access_token + "&openid=" + openid + "&lang=zh_CN"
        f = urllib2.urlopen(url)
        response = f.read()
        result = simplejson.loads(response)
        if 'errcode' in result:
            _logger.error("获取用户详细信息出错!")
            return {"openid": openid}
        else:
            iamgedata = False
            imageurl = result.get('headimgurl', False)
            if imageurl:
                image = urllib2.urlopen(imageurl).read()
                iamgedata = base64.b64encode(image)
            real_result = {}
            real_result.update({
                "openid": result['openid'],
                "name": result['nickname'],
                "image": iamgedata
            })
            return real_result
            # return result

    def getuserdetailinfo_qy(self, url, access_token, userid):
        url = url + "?access_token=" + access_token + "&userid=" + userid
        f = urllib2.urlopen(url)
        response = f.read()
        result = simplejson.loads(response)
        print result
        if result['errcode'] <> 0:
            return {"UserId": userid}
        else:
            iamgedata = False
            imageurl = result.get('avatar', False)
            if imageurl:
                image = urllib2.urlopen(imageurl).read()
                iamgedata = base64.b64encode(image)
            real_result = {}
            real_result.update({
                "UserId": result.get('userid', False),
                "name": result.get('name', False),
                "email": result.get('email', False),
                "image": iamgedata
            })
            return real_result

    def getuserinfo(self, url, code, access_token):
        url = url + "?access_token=" + access_token + "&code=" + code
        f = urllib2.urlopen(url)
        response = f.read()
        result = simplejson.loads(response)
        if 'errcode' in result:
            return {"error": "获取用户信息出错!"}
        else:
            return result

    def _auth_oauth_validate(self, cr, uid, provider, access_token, context=None):
        """ return the validation data corresponding to the access token """
        p = self.pool.get('auth.oauth.provider').browse(cr, uid, provider, context=context)
        if p['provider_type'] == "weixin" or p['provider_type'] == "pc_weixin":
            validation = self.get_access_token(p.validation_endpoint, p.client_id, p.client_sercret, access_token)
        elif p['provider_type'] == 'weixin_qy':
            validation = self.get_qy_access_token(p.validation_endpoint, p.client_id, p.client_sercret, access_token)
        else:
            validation = self._auth_oauth_rpc(cr, uid, p.validation_endpoint, access_token)
        if validation.get("error"):
            raise Exception(validation['error'])
        if p.data_endpoint:
            if p['provider_type'] == "weixin" or p['provider_type'] == "pc_weixin":
                data = self.getuserdetailinfo(p.data_endpoint, validation['access_token'], validation['openid'])
            elif p['provider_type'] == "weixin_qy":
                data = self.getuserdetailinfo_qy(p.data_endpoint, validation['access_token'], validation['UserId'])
            else:
                data = self._auth_oauth_rpc(cr, uid, p.data_endpoint, access_token)
            validation.update(data)
        return validation

    def _auth_oauth_rpc(self, cr, uid, endpoint, access_token, context=None):
        params = werkzeug.url_encode({'access_token': access_token})
        if urlparse.urlparse(endpoint)[4]:
            url = endpoint + '&' + params
        else:
            url = endpoint + '?' + params
        f = urllib2.urlopen(url)
        response = f.read()
        if response.find('callback') == 0:
            response = response[response.index("(") + 1: response.rindex(")")]
        return simplejson.loads(response)

    def get_user_login_info(self, cr, uid, provider, params, context=None):
        access_token = params.get('access_token')
        validation = self._auth_oauth_validate(cr, uid, provider, access_token)
        provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
        provider_type = provider_obj['provider_type']

        if provider_type == 'qq':
            oauth_uid = 'openid'
        elif provider_type == 'weixin' or provider_type == 'pc_weixin':
            oauth_uid = 'openid'
            params.update({
                "access_token": validation['access_token']
            })
            access_token = validation['access_token']
        elif provider_type == "weixin_qy":
            oauth_uid = 'UserId'
            params.update({
                "access_token": validation['access_token']
            })
            access_token = validation['access_token']
        elif provider_type == 'weibo':
            oauth_uid = 'userid'
        else:
            oauth_uid = 'user_id'
        if not validation.get(oauth_uid):
            raise yuancloud.exceptions.AccessDenied()
        return {"validation": validation, "oauth_uid": oauth_uid, "params": params, "access_token": access_token}

    def _auth_oauth_signin(self, cr, uid, provider, validation, params, context=None):

        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: yuancloud.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        try:

            provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
            provider_type = provider_obj['provider_type']

            if provider_type == 'qq':
                oauth_uid = validation['openid']
            elif provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider_type == "pc_weixin":
                oauth_uid = validation['openid']
            elif provider_type == "weixin_qy":
                oauth_uid = validation['UserId']
            elif provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']
            user_ids = self.pool['oauth_provider_entity_extend'].search(cr, SUPERUSER_ID,
                                                                        [("oauth_uid", "=", oauth_uid),
                                                                         ('oauth_provider_id', '=', provider)], context)
            if user_ids:
                assert len(user_ids) == 1
                oauth_provider_info = self.pool['oauth_provider_entity_extend'].browse(cr, SUPERUSER_ID, user_ids[0],
                                                                                       context)
                user = self.browse(cr, uid, oauth_provider_info['res_user_id'].id, context=context)
                try:
                    oauth_provider_info.write({'oauth_access_token': params['access_token']})
                    user.write({'oauth_access_token': params['access_token'], 'oauth_provider_id': provider,
                                'oauth_uid': oauth_uid})
                except Exception as e:
                    _logger.er("更新会话出错:" + str(e))
                return user.login
            else:
                raise yuancloud.exceptions.AccessDenied()
                # user_ids = self.search(cr, uid, [("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
                # if not user_ids:
                #     raise yuancloud.exceptions.AccessDenied()
                # assert len(user_ids) == 1
                # user = self.browse(cr, uid, user_ids[0], context=context)
                #
                # user.write({'oauth_access_token': params['access_token']})
                # return user.login
        except yuancloud.exceptions.AccessDenied, access_denied_exception:
            if context and context.get('no_user_creation'):
                return None
            token = ""
            try:
                state = simplejson.loads(params['state'])
                token = state.get('t', "")
            except:
                pass

            provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
            provider_type = provider_obj['provider_type']

            if provider_type == 'qq':
                oauth_uid = validation['nickname']
            elif provider_type == 'weixin':
                oauth_uid = validation['openid']
            elif provider_type == "pc_weixin":
                oauth_uid = validation['openid']
            elif provider_type == "weixin_qy":
                oauth_uid = validation['UserId']
            elif provider_type == 'weibo':
                oauth_uid = validation['userid']
            else:
                oauth_uid = validation['user_id']
            email = validation.get('email', '%s_%s' % (provider_type, oauth_uid))
            name = validation.get('name', email)
            user_image = validation.get('image', False)
            values = {
                'name': name,
                'login': email,
                'email': email,
                'oauth_provider_id': provider,
                'oauth_uid': oauth_uid,
                'oauth_access_token': params['access_token'],
                'active': True,
                'image': user_image,
            }
            _logger.info(values)
            try:
                _, login, _ = self.signup(cr, uid, values, token, context=context)
                return login
            except SignupError:
                _logger.info(SignupError)
                raise access_denied_exception

    def auth_oauth(self, cr, uid, provider, params, context=None):
        # Advice by Google (to avoid Confused Deputy Problem)
        # if validation.audience != OUR_CLIENT_ID:
        # abort()
        # else:
        # continue with the process
        # access_token = params.get('access_token')
        # validation = self._auth_oauth_validate(cr, uid, provider, access_token)
        #
        # provider_obj = self.pool['auth.oauth.provider'].read(cr, uid, provider, context=context)
        # provider_type = provider_obj['provider_type']
        #
        # if provider_type == 'qq':
        #     oauth_uid = 'openid'
        # elif provider_type == 'weixin':
        #     oauth_uid = 'openid'
        #     params.update({
        #         "access_token": validation['access_token']
        #     })
        #     access_token = validation['access_token']
        # elif provider_type == "weixin_qy":
        #     oauth_uid = 'UserId'
        #     params.update({
        #         "access_token": validation['access_token']
        #     })
        #     access_token = validation['access_token']
        # elif provider_type == 'weibo':
        #     oauth_uid = 'userid'
        # else:
        #     oauth_uid = 'user_id'
        #
        # if not validation.get(oauth_uid):
        #     raise yuancloud.exceptions.AccessDenied()
        # retrieve and sign in user
        validation = params and params.get('validation')
        access_token = params and params.get('access_token')
        if not validation:
            return super(res_users, self).auth_oauth(cr, uid, provider, params, context=context)
        login = self._auth_oauth_signin(cr, uid, provider, validation, params, context=context)
        if not login:
            raise yuancloud.exceptions.AccessDenied()
        # return user credentials
        return (cr.dbname, login, access_token)


class OAuthLogin(Home):
    # 判断网站来自mobile还是pc
    def checkMobile(self, userAgent):
        """
        demo :
            @app.route('/m')
            def is_from_mobile():
                if checkMobile(request):
                    return 'mobile'
                else:
                    return 'pc'
        :param request:
        :return:
        """
        # userAgent = requestinfo.headers['User-Agent']
        # userAgent = env.get('HTTP_USER_AGENT')
        _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
        _long_matches = re.compile(_long_matches, re.IGNORECASE)
        _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
        _short_matches = re.compile(_short_matches, re.IGNORECASE)

        if _long_matches.search(userAgent) != None:
            return True
        user_agent = userAgent[0:4]
        if _short_matches.search(user_agent) != None:
            return True
        return False

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))

        if ('MicroMessenger' in request.httprequest.user_agent.string) and 'oauth_uid' not in kw:
            providers = self.list_providers_type("weixin")
            is_enterprise = kw.get('is_enterprise', False)
            if is_enterprise:
                weixin_provider = ""
                for provider in providers:
                    if provider['provider_type'] == "weixin_qy":
                        weixin_provider = provider
                        break
                if weixin_provider:
                    return werkzeug.utils.redirect(weixin_provider['auth_link'], 303)
            else:
                weixin_provider = ""
                for provider in providers:
                    if provider['provider_type'] == "weixin":
                        weixin_provider = provider
                        break
                if weixin_provider:
                    return werkzeug.utils.redirect(weixin_provider['auth_link'], 303)
        response = super(OAuthLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('oauth_error')
            if error == '1':
                error = _("Sign up is not allowed on this database.")
            elif error == '2':
                error = _("Access Denied")
            elif error == '3':
                error = _(
                    "You do not have access to this database or your invitation has expired. Please ask for an invitation and be sure to follow the link in your invitation email.")
            else:
                error = None
            # for provider in providers:
            #     if provider['provider_type'] == "weixin" or provider['provider_type'] == "weixin_qy":
            #         providers.remove(provider)
            if self.checkMobile(request.httprequest.user_agent.string):
                # for provider in providers:
                #     if provider['provider_type'] == "pc_weixin":
                #         providers.remove(provider)
                providers = self.list_providers_type("mobile")
            else:
                providers = self.list_providers_type("pc")
            response.qcontext['providers'] = providers
            if error:
                response.qcontext['error'] = error
        if 'oauth_uid' in kw and kw[
            'oauth_uid'] and request.httprequest.method == 'POST' and (
                        response.status_code == 303 or response.status_code == 200):
            user = request.registry.get('res.users')

            userids = user.search(request.cr, SUPERUSER_ID, [("login", "=", kw['login'])])
            if userids:
                assert len(userids) == 1
                userinfo = user.browse(request.cr, SUPERUSER_ID, userids[0], context=None)
                request.cr.commit()
                values = {}
                values.update({
                    "oauth_provider_id": kw.get("oauth_provider_id", "")
                })
                values.update({
                    "oauth_uid": kw.get("oauth_uid", "")
                })
                values.update({
                    "oauth_access_token": kw.get("oauth_access_token", "")
                })
                try:
                    userinfo.write(values)
                except Exception as e:
                    _logger.error("更新上次会话出错:" + str(e))
                oauth_provider_entity_values = {}
                oauth_provider_entity_values.update({
                    "res_user_id": userinfo.id,
                    "oauth_provider_id": kw.get("oauth_provider_id", ""),
                    "oauth_uid": kw.get("oauth_uid", ""),
                    "oauth_access_token": kw.get("oauth_access_token", "")
                })
                try:
                    oauth_provider_entity_id = request.registry['oauth_provider_entity_extend'].create(request.cr,
                                                                                                       yuancloud.SUPERUSER_ID,
                                                                                                       oauth_provider_entity_values)
                    print oauth_provider_entity_id
                except Exception as e:
                    _logger.error("创建登录方式出错:" + str(e))
                request.cr.commit()
                # user.updateauthid(request.cr, SUPERUSER_ID, uids[0], values)
                # return werkzeug.utils.redirect('/', 303)
        return response

    def list_providers_type(self, type):
        providers = self.list_providers()
        provider_infos = []
        for provider in providers:
            if provider['provider_browser'] == type:
                provider_infos.append(provider)
        return provider_infos

    def list_providers(self):
        try:
            provider_obj = request.registry.get('auth.oauth.provider')
            providers = provider_obj.search_read(request.cr, SUPERUSER_ID, [('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/signin'
            state = self.get_state(provider)
            state = simplejson.dumps(state).encode('base64').replace('\n', '').rstrip(
                '=')  # json.dumps(state, ensure_ascii=False).encode('utf8')
            print state
            # if request.httprequest.user_agent.platform not in ['android', 'iphone']:
            if provider['provider_type'] <> "weixin" and provider['provider_type'] <> "weixin_qy" and provider[
                'provider_type'] <> "pc_weixin":
                params = dict(
                    debug=request.debug,
                    response_type='token',
                    client_id=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=(state),
                )
            else:
                params = dict(
                    response_type='code',
                    appid=provider['client_id'],
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    state=state,
                )
            provider['auth_link'] = provider['auth_endpoint'] + '?' + werkzeug.url_encode(
                collections.OrderedDict(sorted(params.items(), key=lambda t: t[0])))

        return providers

    def get_state(self, provider):
        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
        # state = dict(
        #     d=request.session.db,
        #     p=provider['id'],
        #     r=werkzeug.url_quote_plus(redirect),
        # )
        state = {}
        state.update({
            "d": request.session.db,
            "p": provider['id'],
            "r": werkzeug.url_quote_plus(redirect)
        })
        token = request.params.get('token')
        if token:
            state.update({
                "t": token
            })
            # state['t'] = token
        return state

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """

        # values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
        values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
        values.update({
            "oauth_provider_id": qcontext.get("oauth_provider_id", "")
        })
        values.update({
            "oauth_uid": qcontext.get("oauth_uid", "")
        })
        values.update({
            "oauth_access_token": qcontext.get("oauth_access_token", "")
        })
        print values
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in
                           request.registry['res.lang'].search_read(request.cr, yuancloud.SUPERUSER_ID, [], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()

    def _signup_with_values(self, token, values):
        db, login, password = request.registry['res.users'].signup(request.cr, yuancloud.SUPERUSER_ID, values, token)
        request.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))
        oauth_provider_entity_values = {}
        oauth_provider_entity_values.update({
            "res_user_id": uid,
            "oauth_provider_id": values.get("oauth_provider_id", ""),
            "oauth_uid": values.get("oauth_uid", ""),
            "oauth_access_token": values.get("oauth_access_token", "")
        })
        try:
            oauth_provider_entity_id = request.registry['oauth_provider_entity_extend'].create(request.cr,
                                                                                               yuancloud.SUPERUSER_ID,
                                                                                               oauth_provider_entity_values)
            print oauth_provider_entity_id
        except Exception as e:
            _logger.error("创建登录方式出错:" + str(e))
        request.cr.commit()
