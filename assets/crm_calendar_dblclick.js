/**
 * CRM calendar — double-click a day cell to open the day-events modal.
 * Writes to dcc.Store crm-cal-selected-day via dash_clientside.set_props.
 */
(function () {
    function bindCalendarDblClick() {
        if (window.__crmCalDblClickBound) {
            return;
        }
        window.__crmCalDblClickBound = true;

        document.body.addEventListener("dblclick", function (e) {
            const inner = e.target.closest(".crm-cal-day-inner[id^='crm-cal-day-']");
            if (!inner || !inner.id) {
                return;
            }
            const date = inner.id.replace("crm-cal-day-", "");
            if (!date) {
                return;
            }
            e.preventDefault();
            if (window.dash_clientside && window.dash_clientside.set_props) {
                window.dash_clientside.set_props("crm-cal-selected-day", {
                    data: { date: date, t: Date.now() },
                });
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindCalendarDblClick);
    } else {
        bindCalendarDblClick();
    }
})();
