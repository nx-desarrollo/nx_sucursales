/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { symmetricalDifference } from "@web/core/utils/arrays";

import { Component, useState } from "@odoo/owl";

export class SwitchBranchMenu extends Component {
    setup() {
        this.branchService = useService("branch");
        this.currentBranch = this.branchService.currentBranch;
        this.state = useState({ branchesToToggle: [] });
    }

    toggleBranch(branchId) {
        this.state.branchesToToggle = symmetricalDifference(this.state.branchesToToggle, [
            branchId,
        ]);
        browser.clearTimeout(this.toggleTimer);
        this.toggleTimer = browser.setTimeout(() => {
            this.branchService.setBranches("toggle", ...this.state.branchesToToggle);
        }, this.constructor.toggleDelay);
    }

    logIntoBranch(branchId) {
        browser.clearTimeout(this.toggleTimer);
        this.branchService.setBranches("loginto", branchId);
    }

    get selectedBranches() {
        return symmetricalDifference(
            this.branchService.allowedBranchIds,
            this.state.branchesToToggle
        );
    }
}
SwitchBranchMenu.template = "web.SwitchBranchMenu";
SwitchBranchMenu.components = { Dropdown, DropdownItem };
SwitchBranchMenu.toggleDelay = 1000;

// export const systrayItem = {
//     Component: SwitchBranchMenu,
//     display: true,
//     display_name: "Cambiar Sucursal",
//     icon: "fa-solid fa-location-dot",
//     sequence: 1,                                

    
// };

// registry.category("systray").add("SwitchBranchMenu", systrayItem, { sequence: 1 });