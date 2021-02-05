# Copyright (C) 2019 Konos
# Copyright (C) 2019 Blanco Martín & Asociados
# Copyright (C) 2019 CubicERP
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, fields


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'etd.mixin']

    def _compute_class_id_domain(self):
        return [('document_type', '=', 'stock_picking')]

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for rec in self:
            auto_sign = rec.company_id.backend_acp_id.auto_sign
            sign = rec._name in [x.model for x in rec.company_id.etd_ids]
            if auto_sign and sign and rec.location_dest_id.usage == 'customer':
                rec.with_delay().document_sign()
        return res

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            if partner and partner.invoicing_policy == 'eguide':
                sii_obj = self.env['sii.document.class']
                sii_document = sii_obj.search(
                    [('name', 'ilike', 'Guía de Despacho Electrónica'),
                     ('prefix', '=', 'GDE'),
                     ('code', '=', 52),
                     ('document_type', '=', 'stock_picking')], limit=1)
                vals.update({'class_id': sii_document and sii_document.id})
        return super(StockPicking, self).create(vals)

    transport_type = fields.Selection(
        [
            ('2', 'Despacho por cuenta de empresa'),
            ('1', 'Despacho por cuenta del cliente'),
            ('3', 'Despacho Externo'),
            ('0', 'Sin Definir')
        ],
        string="Tipo de Despacho",
        default="2",
        readonly=False, states={'done': [('readonly', True)]},
    )

    move_reason = fields.Selection(
        [
            ('1', 'Operación constituye venta'),
            ('2', 'Ventas por efectuar'),
            ('3', 'Consignaciones'),
            ('4', 'Entrega Gratuita'),
            ('5', 'Traslados Internos'),
            ('6', 'Otros traslados no venta'),
            ('7', 'Guía de Devolución'),
            ('8', 'Traslado para exportación'),
            ('9', 'Ventas para exportación')
        ],
        string='Razón del traslado',
        default="2",
        readonly=False, states={'done': [('readonly', False)]},
    )    
