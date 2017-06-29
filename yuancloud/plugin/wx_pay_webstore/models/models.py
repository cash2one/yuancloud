# -*- coding: utf-'8' "-*-"
try:
    import simplejson as json
except ImportError:
    import json
import logging
import urlparse
import urllib2
from lxml import etree
import random
import string
#from yuancloud.addons.wx_base.models.util import util
from yuancloud.addons.payment.models.payment_acquirer import ValidationError
from yuancloud.http import request
from yuancloud import api, fields, models
from yuancloud.osv import orm
from yuancloud import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class AcquirerWeixin(models.Model):
    _inherit = 'payment.acquirer'

    def _get_ipaddress(self):
        return "127.0.0.1"#self.ip_address

    @api.model
    def _get_providers(self):
        providers = super(AcquirerWeixin, self)._get_providers()
        providers.append(['weixin', 'weixin'])
        return providers

    weixin_officialaccount=fields.Many2one('wx.officialaccount',string="微信服务号")

    #
    def _get_weixin_urls(self, environment):
        if environment == 'prod':
            return {
                'weixin_url': 'https://api.mch.weixin.qq.com/pay/unifiedorder'
            }
        else:
            return {
                'weixin_url': 'https://api.mch.weixin.qq.com/pay/unifiedorder'
            }
    #
    # @api.one
    # def _get_weixin_key(self):
    #     return self.weixin_key
    #
    _defaults = {
        'fees_active': False,
    }


    def random_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join([random.choice(chars) for n in xrange(size)])

    def weixin_compute_fees(self, cr, uid, id, amount, currency_id, country_id, context=None):
        """ Compute paypal fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        acquirer = self.browse(cr, uid, id, context=context)
        if not acquirer.fees_active:
            return 0.0
        country = self.pool['res.country'].browse(cr, uid, country_id, context=context)
        if country and acquirer.company_id.country_id.id == country.id:
            percentage = acquirer.fees_dom_var
            fixed = acquirer.fees_dom_fixed
        else:
            percentage = acquirer.fees_int_var
            fixed = acquirer.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed ) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def weixin_form_generate_values(self,tx_values):
        self.ensure_one()
        weixin_tx_values = dict(tx_values)
        if 'MicroMessenger' in request.httprequest.user_agent.string:
            trade_type="JSAPI"
        else:
            trade_type="NATIVE"
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        amount = int(tx_values.get('amount', 0) * 100)
        nonce_str = self.random_generator()
        weixin_tx_values.update(
            {
                'appid': self.weixin_officialaccount.wx_appid,
                'mch_id': self.weixin_officialaccount.wx_mch_id,
                'nonce_str': nonce_str,
                'body': tx_values['reference'],
                'out_trade_no': tx_values['reference'],
                'total_fee': amount,
                'spbill_create_ip': self._get_ipaddress(),
                'notify_url': '%s' %urlparse.urljoin(base_url,""),
                'trade_type': trade_type,
                'product_id': tx_values['reference'],
            }
        )
        weixin_tx_values['process_url'] = self._get_weixin_urls(self.environment)['weixin_url']
        weixin_tx_values['data_xml']=""
        #weixin_tx_values['appkey'] = self.weixin_officialaccount.wx_mch_secret
        weixin_tx_values['data_xml']=""
        return  weixin_tx_values

    @api.multi
    def weixin_get_form_action_url(self):
        self.ensure_one()
        return '/payment/weixin/process'

class TxWeixin(models.Model):
    _inherit = 'payment.transaction'

    weixin_txn_id = fields.Char(string='Transaction ID')
    weixin_txn_type = fields.Char(string='Transaction type')


    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    def _weixin_form_get_tx_from_data(self,cr,uid, data,context=None):
        reference, txn_id = data.get('out_trade_no'), data.get('out_trade_no')
        if not reference or not txn_id:
            error_msg = 'weixin: received data with missing reference (%s) or txn_id (%s)' % (reference, txn_id)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx_ids = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', reference)], context=context)
        #tx_ids2 = self.search(cr, uid, [('reference', '=', reference)], context=context)
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'weixin: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return self.browse(cr, uid, tx_ids[0], context=context)
        #return tx_ids[0]

    def _weixin_form_validate(self, cr, uid, tx, data, context=None):
        status = data.get('result_code')
        data = {
            'acquirer_reference': data.get('out_trade_no'),
            'weixin_txn_id': data.get('transaction_id'),
            'weixin_txn_type': data.get('fee_type'),
        }
        if status == "SUCCESS":
            _logger.info('Validated weixin payment for tx %s: set as done' % (tx.reference))
            data.update(state='done', date_validate=data.get('time_end', fields.datetime.now()))
            return tx.write(data)
        else:
            error = 'Received unrecognized status for weixin payment %s: %s, set as error' % (tx.reference, status)
            _logger.info(error)
            data.update(state='error', state_message=error)
            return tx.write(data)

class website(orm.Model):
    _inherit = 'website'

    def sale_get_order(self, cr, uid, ids, force_create=False, code=None, update_pricelist=False, force_pricelist=False, context=None):
        """ Return the current sale order after mofications specified by params.

        :param bool force_create: Create sale order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sale order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one

        :returns: browse record for the current sale order
        """
        partner = self.get_partner(cr, uid)
        sale_order_obj = self.pool['sale.order']
        sale_order_id = request.session.get('sale_order_id') #or (partner.last_website_so_id.id if partner.last_website_so_id and partner.last_website_so_id.state == 'draft' else False)

        sale_order = None
        # Test validity of the sale_order_id
        if sale_order_id and sale_order_obj.exists(cr, SUPERUSER_ID, sale_order_id, context=context):
            sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        else:
            sale_order_id = None
        pricelist_id = request.session.get('website_sale_current_pl')

        if force_pricelist and self.pool['product.pricelist'].search_count(cr, uid, [('id', '=', force_pricelist)], context=context):
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True

        # create so if needed
        if not sale_order_id and (force_create or code):
            # TODO cache partner_id session
            user_obj = self.pool['res.users']
            affiliate_id = request.session.get('affiliate_id')
            salesperson_id = affiliate_id if user_obj.exists(cr, SUPERUSER_ID, affiliate_id, context=context) else request.website.salesperson_id.id
            for w in self.browse(cr, uid, ids):
                addr = partner.address_get(['delivery', 'invoice'])
                values = {
                    'partner_id': partner.id,
                    'pricelist_id': pricelist_id,
                    'payment_term_id': partner.property_payment_term_id.id if partner.property_payment_term_id else False,
                    'team_id': w.salesteam_id.id,
                    'partner_invoice_id': addr['invoice'],
                    'partner_shipping_id': addr['delivery'],
                    'user_id': salesperson_id or w.salesperson_id.id,
                }
                sale_order_id = sale_order_obj.create(cr, SUPERUSER_ID, values, context=context)
                request.session['sale_order_id'] = sale_order_id
                sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)

                if request.website.partner_id.id != partner.id:
                    self.pool['res.partner'].write(cr, SUPERUSER_ID, partner.id, {'last_website_so_id': sale_order_id})

        if sale_order_id:

            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id and sale_order.fiscal_position_id.id or False

                # change the partner, and trigger the onchange
                sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], {'partner_id': partner.id}, context=context)
                sale_order_obj.onchange_partner_id(cr, SUPERUSER_ID, [sale_order_id], context=context)

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True

                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order_obj.write(cr, SUPERUSER_ID, [sale_order_id], values, context=context)

                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id and sale_order.fiscal_position_id.id or False
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True

            if code and code != sale_order.pricelist_id.code:
                pricelist_ids = self.pool['product.pricelist'].search(cr, uid, [('code', '=', code)], limit=1, context=context)
                if pricelist_ids:
                    pricelist_id = pricelist_ids[0]
                    update_pricelist = True
            elif code is not None and sale_order.pricelist_id.code:
                # code is not None when user removes code and click on "Apply"
                pricelist_id = partner.property_product_pricelist.id
                update_pricelist = True

            # update the pricelist
            if update_pricelist:
                request.session['website_sale_current_pl'] = pricelist_id
                values = {'pricelist_id': pricelist_id}
                sale_order.write(values)
                for line in sale_order.order_line:
                    if line.exists():
                        sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)

            # update browse record
            if (code and code != sale_order.pricelist_id.code) or sale_order.partner_id.id != partner.id or force_pricelist:
                sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order.id, context=context)

        else:
            request.session['sale_order_id'] = None
            return None

        return sale_order
