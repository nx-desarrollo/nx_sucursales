/** @odoo-module **/

import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

console.log('"SwitchBranchMenu" component applied');
export class SwitchBranchMenu extends Component {
    setup() {
        this.branchService = useService("branch");
    }

    async logIntoBranch(branchId) {
        await rpc("/set_branch", { branch_id: branchId });
        this.branchService.setBranch(branchId);
    }
}

SwitchBranchMenu.template = "branch.SwitchBranchMenu";
SwitchBranchMenu.components = { Dropdown, DropdownItem };
SwitchBranchMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: SwitchBranchMenu,
    isDisplayed(env) {
        const { availableBranches } = env.services.branch;
        return Object.keys(availableBranches).length > 1;
    },
};

registry.category("systray").add("SwitchBranchMenu", systrayItem, { sequence: 1 });