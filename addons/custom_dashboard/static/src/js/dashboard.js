import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { View } from "@web/views/view";

export class CustomDashboard extends Component {
    static template = "custom_dashboard.Dashboard";
    static components = { View };
    get confirmaComercialProps() {
        const hoy = new Date();
        const desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01 00:00:00`;
        return {
            type: "graph",
            resModel: "legos18.crm.confirma.report",
            domain: [['fecha_entrada', '>=', desde]],
            groupBy: ['user_id'],
            noBreadcrumbs: true,
            display: { controlPanel: false },
        };
    }
    
    get confirmaOrigenProps() {
        const hoy = new Date();
        const desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01 00:00:00`;
        return {
            type: "graph",
            resModel: "legos18.crm.confirma.report",
            domain: [['fecha_entrada', '>=', desde]],
            groupBy: ['source_id'],
            noBreadcrumbs: true,
            display: { controlPanel: false },
        };
    }
    
    get confirmaReferidoProps() {
        const hoy = new Date();
        const desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01 00:00:00`;
        return {
            type: "graph",
            resModel: "legos18.crm.confirma.report",
            domain: [['fecha_entrada', '>=', desde]],
            groupBy: ['referido'],
            noBreadcrumbs: true,
            display: { controlPanel: false },
        };
    }

    get equipoIngresoProps() {
        const hoy = new Date();
        const desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01 00:00:00`;
        return {
            type: "graph",
            resModel: "legos18.crm.stage.mov",
            domain: [["user_id", "in", [8, 13]], ["fecha", ">=", desde]],
            noBreadcrumbs: true,
            display: { controlPanel: false },
        };
    }

    get equipoCierreProps() {
        const hoy = new Date();
        const desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01 00:00:00`;
        return {
            type: "graph",
            resModel: "legos18.crm.stage.mov",
            domain: [["user_id", "in", [7, 10]], ["fecha", ">=", desde]],
            noBreadcrumbs: true,
            display: { controlPanel: false },
        };
    }

}

registry.category("actions").add("custom_dashboard.Dashboard", CustomDashboard);
