/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";

class Legos18CrmConfirmaReportListController extends ListController {
    openRecord(record) {
        const allIds = this.model.root.records.map((r) => r.resId);
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "crm.lead",
                views: [[false, "form"]],
                target: "current",
            },
            {
                props: {
                    resId: record.resId,
                    resIds: allIds,
                },
            }
        );
    }
}

registry.category("views").add("legos18_confirma_list", {
    ...listView,
    Controller: Legos18CrmConfirmaReportListController,
});
