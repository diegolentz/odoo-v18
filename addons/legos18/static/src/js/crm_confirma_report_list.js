/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { ListRenderer } from "@web/views/list/list_renderer";

class Legos18CrmConfirmaReportListRenderer extends ListRenderer {
    async onCellClicked(record, column, ev) {
        // La lista es editable: un clic en una celda entra en edicion y nunca llega a
        // openRecord. La columna de la oportunidad abre el lead con el paginador.
        if (column.name === "lead_id") {
            return this.props.openRecord(record);
        }
        return super.onCellClicked(record, column, ev);
    }
}

class Legos18CrmConfirmaReportListController extends ListController {
    /** Ids de todos los registros de la lista (no solo la pagina cargada ni los grupos abiertos). */
    async _getAllResIds() {
        const root = this.model.root;
        if (!root.isGrouped) {
            const loaded = root.records.map((r) => r.resId);
            if (loaded.length >= root.count) {
                return loaded;
            }
        }
        const order = root.orderBy
            .map((o) => `${o.name}${o.asc ? "" : " desc"}`)
            .join(", ");
        return this.model.orm.search(root.resModel, root.domain, {
            limit: this.model.activeIdsLimit,
            context: root.context,
            order: order || undefined,
        });
    }

    async openRecord(record) {
        // El id del informe coincide con el id del lead (id = msg.res_id en la SQL view).
        const resIds = await this._getAllResIds();
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                res_model: "crm.lead",
                views: [[false, "form"]],
                target: "current",
            },
            {
                props: {
                    resId: record.data.lead_id?.id || record.resId,
                    resIds,
                },
            }
        );
    }
}

registry.category("views").add("legos18_confirma_list", {
    ...listView,
    Controller: Legos18CrmConfirmaReportListController,
    Renderer: Legos18CrmConfirmaReportListRenderer,
});
