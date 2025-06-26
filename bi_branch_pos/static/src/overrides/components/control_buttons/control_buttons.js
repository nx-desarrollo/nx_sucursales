/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { useService } from "@web/core/utils/hooks";

// Método get_pos_branch_ids dentro del mismo archivo
async function getPosBranchIds(posConfigId) {
    const ormService = useService("orm");
    try {
        // Realizamos la llamada ORM para obtener las sucursales asociadas a la configuración POS
        const result = await ormService.call("pos.config", "get_pos_branch_ids", [[posConfigId]]);
        
        // Verificamos si el resultado es un array y extraemos los IDs de las sucursales
        if (Array.isArray(result)) {
            const branchIds = result.map((branch) => branch.id);
            console.log("✅ Sucursales obtenidas:", branchIds);
            return branchIds;
        } else {
            console.error("❌ Resultado inesperado de la consulta:", result);
            return [];
        }
    } catch (error) {
        console.error("❌ Error al consultar sucursales:", error);
        return [];
    }
}

patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        this.branchIds = [];  // Variable para almacenar las sucursales
        const posConfigId = this.pos.config?.id;

        console.log("🧪 ID de pos.config:", posConfigId);

        if (posConfigId) {
            // Realizamos la consulta de las sucursales en setup
            getPosBranchIds(posConfigId)
                .then((branchIds) => {
                    this.branchIds = branchIds;
                    console.log("✔️ Sucursales obtenidas en setup:", this.branchIds);
                })
                .catch((error) => {
                    console.error("❌ Error al obtener las sucursales en setup:", error);
                });
        } else {
            console.log("❌ No se pudo obtener el ID de pos.config");
        }
    },

    onClickQuotation() {
        console.log("🟡 Evento: onClickQuotation interceptado");

        // Verificamos si tenemos sucursales disponibles
        if (this.branchIds.length === 0) {
            console.log("❌ No se encontraron sucursales.");
            return;
        }

        // Lanzamos el diálogo con el filtro de sucursales
        this.dialog.add(SelectCreateDialog, {
            resModel: "sale.order",
            noCreate: true,
            multiSelect: false,
            domain: [
                ["state", "!=", "cancel"],
                ["invoice_status", "!=", "invoiced"],
                ["currency_id", "=", this.pos.currency.id],
                ["branch_id", "in", this.branchIds],
            ],
            onSelected: async (resIds) => {
                if (resIds.length) {
                    await this.pos.onClickSaleOrder(resIds[0]);
                }
            },
        });
    },
});
