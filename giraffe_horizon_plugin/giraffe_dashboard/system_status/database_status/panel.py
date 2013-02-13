import horizon
from horizon.dashboards.nova import dashboard


class DatabaseStatusPanel(horizon.Panel):
    name = "Database Status"
    slug = 'database_status'

dashboard.Nova.register(DatabaseStatusPanel)
