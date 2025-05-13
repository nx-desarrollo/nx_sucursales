/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { symmetricalDifference } from "@web/core/utils/arrays";
import { session } from "@web/session";
var ajax = require('web.ajax');

function parseBranchIds(bidsFromHash) {
    const bids = [];
    if (typeof bidsFromHash === "string") {
        bids.push(...bidsFromHash.split(",").map(Number));
    } else if (typeof bidsFromHash === "number") {
        bids.push(bidsFromHash);
    }
    return bids;
}

function computeAllowedBranchIds(bids, availableBranches, currentCompanyId) {
    let availableBranchIds = Object.values(availableBranches).sort((a, b) => a.sequence - b.sequence).map((branch) => branch.id);
    let allowedBranchIds = (bids || []).filter((id) => availableBranchIds.includes(id) && availableBranches[id].company === currentCompanyId);
    if (!allowedBranchIds.length) {
        allowedBranchIds = [availableBranchIds[0]];
    }
    return allowedBranchIds;
}

export const branchService = {
    dependencies: ["user", "router", "cookie"],
    start(env, { user, router, cookie }) {
        let bids = [];
        if ("bids" in router.current.hash) {
            bids = parseBranchIds(router.current.hash.bids);
        } else if ("bids" in cookie.current) {
            bids = parseBranchIds(cookie.current.bids);
        }

        let sequence = 0;
        const allowedCompanyIds = env.services.company.allowedCompanyIds;
        const availableBranches = {};
        for (const companyId of allowedCompanyIds) {
            for(const [key, value] of Object.entries(session.user_branches.allowed_branches)) {
                if (value.company === companyId) {
                    availableBranches[key] = { sequence, ...value };
                    sequence++;
                }
            }
        }

        let allowedBranchIds = computeAllowedBranchIds(bids, availableBranches, allowedCompanyIds[0]);
        ajax.jsonRpc('/set_brnach', 'call', {'user': user.userId, 'branch': allowedBranchIds[0]});

        const stringBIds = allowedBranchIds.join(",");
        router.replaceState({ bids: stringBIds }, { lock: true });
        cookie.setCookie("bids", stringBIds);

        user.updateContext({ allowed_branch_ids: allowedBranchIds });

        return {
            availableBranches,
            get allowedBranchIds() {
                return allowedBranchIds.slice();
            },
            get currentBranch() {
                return availableBranches[allowedBranchIds[0]];
            },
            setBranches(mode, ...branchIds) {
                // compute next branch ids
                let nextBranchIds;
                if (mode === "toggle") {
                    nextBranchIds = symmetricalDifference(allowedBranchIds, branchIds);
                } else if (mode === "loginto") {
                    const branchId = branchIds[0];
                    if (allowedBranchIds.length === 1) {
                        // 1 enabled branch: stay in single branch mode
                        nextBranchIds = [branchId];
                    } else {
                        // multi branch mode
                        nextBranchIds = [
                            branchId,
                            ...allowedBranchIds.filter((id) => id !== branchId),
                        ];
                    }
                }
                nextBranchIds = nextBranchIds.length ? nextBranchIds : [branchIds[0]];
                const branchCompanyId = availableBranches[nextBranchIds[0]].company
                // apply them
                if (branchCompanyId !== allowedCompanyIds[0]) {
                    const nextCompanyIds = [
                        branchCompanyId,
                        ...allowedCompanyIds.filter((id) => id !== branchCompanyId),
                    ];
                    router.pushState({ cids: nextCompanyIds, bids: nextBranchIds }, { lock: true });
                    cookie.setCookie("cids", nextCompanyIds);
                    cookie.setCookie("bids", nextBranchIds);
                }
                else {
                    router.pushState({ bids: nextBranchIds }, { lock: true });
                    cookie.setCookie("bids", nextBranchIds);
                }
                browser.setTimeout(() => browser.location.reload()); // history.pushState is a little async
            },
        };
    },
};

registry.category("services").add("branch", branchService);