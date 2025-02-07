odoo.define('kbt_account_ext.account_group_selection', function (require) {
  "use strict";

      var core = require('web.core');
      var relational_fields = require('web.relational_fields');
      var _t = core._t;
      var registry = require('web.field_registry');


      var FieldSelection = relational_fields.FieldSelection;

      var qweb = core.qweb;

      var HierarchySelection = FieldSelection.extend({
          _renderEdit: function () {
              var self = this;
              var prom = Promise.resolve()
              if (!self.hierarchy_groups) {
                  prom = this._rpc({
                      model: 'account.account.group',
                      method: 'search_read',
                      kwargs: {
                          domain: [],
                          fields: ['id', 'internal_group', 'display_name'],
                      },
                  }).then(function(arg) {
                      self.values = _.map(arg, v => [v['id'], v['display_name']])
                      self.hierarchy_groups = [
                          {'name': _t('Net Sales'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_sales'), v => v['id'])},
                          {'name': _t('Net Revenue From Sales'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_revenue_from_sales'), v => v['id'])},
                          {'name': _t('Contribution At Std Var Cost'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'contribution_at_std_var_cost'), v => v['id'])},
                          {'name': _t('Net Contribution'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_contribution'), v => v['id'])},
                          {'name': _t('Gross Profit'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'gross_profit'), v => v['id'])},
                          {'name': _t('Net Profit Before Interest'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_profit_before_interest'), v => v['id'])},
                          {'name': _t('Net Profit Loss Before Tax Kin'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_profit_loss_before_tax_kin'), v => v['id'])},
                          {'name': _t('Net Profit Loss After Income Tax Kin'), 'ids': _.map(_.filter(arg, v => v['internal_group'] == 'net_profit_loss_after_income_tax_kin'), v => v['id'])},
                      ]
                  });
              }

              Promise.resolve(prom).then(function() {
                  self.$el.empty();
                  self._addHierarchy(self.$el, self.hierarchy_groups, 0);
                  var value = self.value;
                  if (self.field.type === 'many2one' && value) {
                      value = value.data.id;
                  }
                  self.$el.val(JSON.stringify(value));
              });
          },
          _addHierarchy: function(el, group, level) {
              var self = this;
              _.each(group, function(item) {
                  var optgroup = $('<optgroup/>').attr(({
                      'label': $('<div/>').html('&nbsp;'.repeat(6 * level) + item['name']).text(),
                  }))
                  _.each(item['ids'], function(id) {
                      var value = _.find(self.values, v => v[0] == id)
                      optgroup.append($('<option/>', {
                          value: JSON.stringify(value[0]),
                          text: value[1],
                      }));
                  })
                  el.append(optgroup)
                  if (item['children']) {
                      self._addHierarchy(el, item['children'], level + 1);
                  }
              })
          }
      });
      registry.add("account_group_selection", HierarchySelection);
  });
