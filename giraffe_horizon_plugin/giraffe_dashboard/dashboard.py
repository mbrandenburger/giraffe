from django.utils.translation import ugettext as _

import horizon


class AdminPanels(horizon.PanelGroup):
    slug = "giraffe_admin"
    name = _("Admin Tools")
#   panels = ('system_status', 'hosts', 'projects', 'meters',)
    panels = ('system_status', 'hosts', 'meters',)


class BillingPanels(horizon.PanelGroup):
    slug = "giraffe_billing"
    name = _("Billing Information")
    # note: the comma at the end DOES make a difference -
    # without it, a PanelGroup with only one panel is not displayed!
    panels = ('billing',)


class GiraffePlugin(horizon.Dashboard):
    name = _("Giraffe")
    slug = "giraffe_dashboard"
    # panels = (BillingPanels, AdminPanels,)
    panels = (AdminPanels,)
    # ^note: the comma at the end DOES make a difference -
    #        without it, the last PanelGroup is not displayed at all!
    default_panel = 'system_status'
    nav = False
    supports_tenants = True


horizon.register(GiraffePlugin)
