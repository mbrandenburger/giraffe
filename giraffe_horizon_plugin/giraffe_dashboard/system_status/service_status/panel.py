import horizon
from horizon.dashboards.nova import dashboard


class ServiceStatusPanel(horizon.Panel):
    name = "Service Status"
    slug = 'sevice_status'

dashboard.Nova.register(ServiceStatusPanel)
