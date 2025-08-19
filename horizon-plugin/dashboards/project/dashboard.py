from django.utils.translation import ugettext_lazy as _
import horizon

class ProjectSIEMDashboard(horizon.Dashboard):
    name = _("SIEM Dashboard")
    slug = "siem_dashboard"
    panels = ('siem_dashboard',)
    default_panel = 'siem_dashboard'

horizon.register(ProjectSIEMDashboard)
