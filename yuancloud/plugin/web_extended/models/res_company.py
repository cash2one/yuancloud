# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json  # noqa
import urllib
import datetime
from yuancloud.osv import osv, fields
from yuancloud import tools, models, api
from yuancloud.tools.translate import _
import werkzeug


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


def geo_find(addr):
    url = 'http://apis.map.qq.com/ws/geocoder/v1/?key=OB4BZ-D4W3U-B7VVO-4PJWW-6TKDJ-WPB77&'
    url += urllib.quote(addr.encode('utf8'))

    try:
        result = json.load(urllib.urlopen(url))
    except Exception, e:
        raise osv.except_osv(_('Network error'),
                             _(
                                 'Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None

    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))


class res_partner(osv.osv):
    _inherit = "res.company"

    _columns = {
        'geo_latitude': fields.float('维度', digits=(16, 5)),
        'geo_longitude': fields.float('经度', digits=(16, 5)),
        'date_localization': fields.date('更新日期'),
    }

    @api.model
    def tencent_map_img(self, zoom=15, width=298, height=298):
        params = {
            'center': '%s,%s' % (str(self.geo_longitude), str(self.geo_latitude)),
            'size': "%d*%d" % (width, height),
            'markers': '%s,%s' % (str(self.geo_longitude), str(self.geo_latitude)),
            'zoom': zoom,
        }
        return urlplus('http://st.map.qq.com/api', params)

    @api.model
    def tencent_map_link(self, zoom=10):
        params = {
            'marker': 'coord:%s,%s;title:%s;addr:%s' % (
                str(self.geo_latitude), str(self.geo_longitude), self.name, self.name),
        }
        # marker=coord:
        return urlplus('http://apis.map.qq.com/uri/v1/marker', params)
        # def geo_localize(self, cr, uid, ids, context=None):
        #     # Don't pass context to browse()! We need country names in english below
        #     for partner in self.browse(cr, uid, ids):
        #         if not partner:
        #             continue
        #         result = geo_find(geo_query_address(street=partner.street,
        #                                             zip=partner.zip,
        #                                             city=partner.city,
        #                                             state=partner.state_id.name,
        #                                             country=partner.country_id.name))
        #         if result:
        #             self.write(cr, uid, [partner.id], {
        #                 'partner_latitude': result[0],
        #                 'partner_longitude': result[1],
        #                 'date_localization': fields.date.context_today(self, cr, uid, context=context)
        #             }, context=context)
        #     return True


class company_geo(osv.TransientModel):
    _name = 'web_extended.map'

    _columns = {
        'addr': fields.char('address'),
        'company_id': fields.many2one('res.company'),
        'geo_latitude': fields.float('Geo Latitude', digits=(16, 5),
                                     default=lambda self: self._get_location('geo_latitude')),
        'geo_longitude': fields.float('Geo Longitude', digits=(16, 5),
                                      default=lambda self: self._get_location('geo_longitude')),
        'date_localization': fields.date('Geo Localization Date', default=lambda self: datetime.datetime.now()),
    }

    @api.model
    def _get_location(self, field):
        company_id = self._context.get('active_id')
        if company_id:
            company = self.env['res.company'].search([('id', '=', company_id)])
            if company:
                return company[field]

    @api.model
    def create(self, vals):
        vals['company_id'] = self._context['active_id']
        return super(company_geo, self).create(vals)

    @api.one
    def apply(self):
        self.company_id.write(
            {"geo_latitude": self.geo_latitude, "geo_longitude": self.geo_longitude,
             "date_localization": datetime.datetime.now()})
