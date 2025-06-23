odoo.define('bi_branch_pos.pos_extended', function (require) {
    "use strict";

    const { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrderLine = (Order) => class PosOrderLine extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.branch_id = this.branch_id || "";
            console.log('------------------> this ', this);
            console.log('1------------------> this.branch_id ', this.branch_id);
        }

        set_branch(branch_id) {
            this.branch_id = branch_id;
            console.log('2------------------> this.branch_id ', this.branch_id);
        }

        get_branch() {
            return this.branch_id;
        }

        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.branch_id = json.branch_id || "";
        }

        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.branch_id = this.get_branch() || "";
            console.log('------------------> this ', this);
            console.log('3------------------> json.branch_id ', json.branch_id);
            return json;
        }

        export_for_printing() {
            const json = super.export_for_printing(...arguments);
            json.branch_id = this.get_branch() || "";
            console.log('4------------------> json.branch_id ', json.branch_id);
            return json;
        }

    }

    Registries.Model.extend(Order, PosOrderLine);
});

