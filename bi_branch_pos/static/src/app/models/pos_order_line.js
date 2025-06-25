/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setup() {
        super.setup(...arguments);
        // Inicializa branch_id
        this.branch_id = this.branch_id || null;
        console.log('------------------> this ', this);
        console.log('1------------------> this.branch_id ', this.branch_id);        
    },

    // Métodos para asignar y obtener la sucursal
    set_branch(branch_id) {
        this.branch_id = branch_id;
        console.log('2------------------> this.branch_id ', this.branch_id);
    },

    get_branch() {
        return this.branch_id;
    },

    // Al importar desde JSON (por ejemplo, reabrir una sesión)
    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.branch_id = json.branch_id || null;
    },

    // Exportar al backend o guardar localmente
    export_as_JSON() {
        const json = super.export_as_JSON();
        json.branch_id = this.branch_id || null;
        console.log('------------------> this ', this);
        console.log('3------------------> json.branch_id ', json.branch_id);        
        return json;        
    },

    // Impresión del ticket
    export_for_printing() {
        const json = super.export_for_printing();
        json.branch_id = this.branch_id || null;
        console.log('4------------------> json.branch_id ', json.branch_id);
        return json;
    },
});
