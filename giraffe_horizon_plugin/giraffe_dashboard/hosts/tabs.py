from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tabs

from horizon.api.base import APIDictWrapper


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = 'giraffe_dashboard/hosts/_detail_overview.html'

    def get_context_data(self, request):
        host_id = self.tab_group.kwargs['host_id']
#        image_id = self.tab_group.kwargs['image_id']
        try:
            host = APIDictWrapper({'id': 123,
                                   'name': 'fake_host',
                                   'activity': '2013-02-01 12:13:14',
                                   'some_attr': 'some random attribute..'})
#            image = api.glance.image_get_meta(self.request, image_id)
        except:
            redirect = reverse('horizon:giraffe_dashboard:hosts:index')
            exceptions.handle(request,
                              _('Unable to retrieve host details.'),
                              redirect=redirect)
        return {'host': host}


class HostDetailTabs(tabs.TabGroup):
    slug = "host_details"
    tabs = (OverviewTab,)
