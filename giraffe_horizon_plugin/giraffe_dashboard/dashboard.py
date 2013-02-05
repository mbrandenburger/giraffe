from django.utils.translation import ugettext as _

import horizon


class BasePanels(horizon.PanelGroup):
    slug = "giraffe_info"
    name = _("Giraffe Information")
    panels = ('overview', 'hosts',)


class SpecialPanels(horizon.PanelGroup):
    slug = "special"
    name = _("Special Information")
    # note: the comma at the end DOES make a difference -
    # without it, a PanelGroup with only one panel is not displayed!
    panels = ('cats',)


class GiraffePlugin(horizon.Dashboard):
    name = _("Giraffe")
    slug = "giraffe_dashboard"
    # note: the comma at the end DOES make a difference -
    # without it, the last PanelGroup is not displayed at all!
    panels = (BasePanels, SpecialPanels,)
    default_panel = 'overview'
    nav = False


horizon.register(GiraffePlugin)
