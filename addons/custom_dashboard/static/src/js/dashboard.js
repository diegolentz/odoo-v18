import {registry} from "@web/core/registry";
import {Component} from "@odoo/owl";
import {View} from "@web/views/view";

export class CustomDashboard extends Component {
    static template = "custom_dashboard.Dashboard";
    static components = {View};
    
    get confirmaGraphProps() {
        return {type: "graph", resModel: "legos18.crm.confirma.report"};
    }
    get confirmaPivotProps() {
        return {type: "pivot", resModel: "legos18.crm.confirma.report"};
    }
    get leadsEtapaProps() {
        return {type: "graph", resModel: "crm.lead", context: {group_by: "stage_id"}};
    }
    get actividadesProps() {
        return {type: "list", resModel: "mail.activity"};
    }

}

registry.category("actions").add("custom_dashboard.Dashboard", CustomDashboard);
// todos los mensuakles, el de las chicas y el editing