/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { AttachmentList } from "@mail/core/common/attachment_list";
import { rpc } from "@web/core/network/rpc";

patch(AttachmentList.prototype, {
    async onClickGenerateSignLink(attachment) {
        const result = await rpc("/sign_pdf/generate_link", {
            attachment_id: attachment.id,
        });
        if (result.error) {
            this.env.services.notification.add("Error: " + result.error, { type: "danger" });
            return;
        }
        navigator.clipboard.writeText(result.url);
        this.env.services.notification.add("🔗 Link copiado: " + result.url, { type: "success" });
    },
});