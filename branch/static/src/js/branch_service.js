/** @odoo-module **/

import { user } from "@web/core/user";
import { router } from "@web/core/browser/router";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { cookie } from "@web/core/browser/cookie";

function parseBranchIds(bids) {
    const ids = [];

    if (typeof bids === "string") {
        ids.push(...bids.split(",").map(Number));
    } else if (typeof bids === "number") {
        ids.push(bids);
    }

    return ids;
}

export const branchService = {
    start() {
        const { user_branches } = session;

        // Caso sin sucursales definidas
        if (!user_branches || !user_branches.allowed_branches?.length) {
            console.log("No hay sucursales definidas para el usuario.");
            return {
                availableBranches: [],
                get allowedBranchIds() {
                    return [];
                },
                get currentBranch() {
                    return null;
                },
                setBranch() {
                    console.log("No se puede cambiar de sucursal: ninguna definida.");
                },
            };
        }

        let bids;
        const hash = router?.current?.hash || {};
        if ("bids" in hash) {
            bids = parseBranchIds(hash.bids);
        } else if ("bids" in cookie) {
            bids = parseBranchIds(cookie.bids);
        }

        const allowedBranchIds = user_branches.allowed_branches.map(({ id }) => id);
        const stringBranchIds = allowedBranchIds.join(",");

        router.replaceState({ bids: stringBranchIds }, { lock: true });
        cookie.set("bids", stringBranchIds);

        user.updateContext({ allowed_branch_ids: allowedBranchIds });

        const availableBranches = user_branches.allowed_branches;

        return {
            availableBranches,
            get allowedBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                return user_branches.allowed_branches.find(({ id }) => id === user_branches.current_branch) || null;
            },
            setBranch(branchId) {
                router.pushState({ bids: [branchId] }, { lock: true });
                cookie.set("bids", [branchId]);
                window.setTimeout(() => window.location.reload(), 1500);
            },
        };
    },
};

registry.category("services").add("branch", branchService);