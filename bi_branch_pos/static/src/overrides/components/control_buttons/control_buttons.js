/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";

// Guarda el original
const originalClickQuotation = ControlButtons.prototype.onClickQuotation;

console.log("Aplicando control_buttons de bi_branch_pos...");

patch(ControlButtons.prototype, {
    async onClickQuotation() {
        console.log("this.pos.config:", this.pos.config);
        const branch_ids = this.pos.config.pos_branch_ids?.map((b) => b.id) || [];
        console.log("branch_ids:", branch_ids);

        // Si hay sucursales, usamos filtro propio
        if (branch_ids.length > 0) {
            alert("Test 2 - bi_branch_pos usando branch_ids");

            this.dialog.add(SelectCreateDialog, {
                resModel: "sale.order",
                noCreate: true,
                multiSelect: false,
                domain: [
                    ["state", "!=", "cancel"],
                    ["invoice_status", "!=", "invoiced"],
                    ["currency_id", "=", this.pos.currency.id],
                    ["branch_id", "in", branch_ids],
                ],
                onSelected: async (resIds) => {
                    if (resIds.length) {
                        await this.pos.onClickSaleOrder(resIds[0]);
                    }
                },
            });
        } else {
            // Si no hay branch_ids, delegamos al original
            if (originalClickQuotation) {
                console.log("Delegando al original de pos_dual_currency...");
                return originalClickQuotation.call(this);
            }
        }
    },
});
