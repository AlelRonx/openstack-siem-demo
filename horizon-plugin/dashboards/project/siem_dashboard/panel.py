from django.utils.translation import ugettext_lazy as _
import horizon

class SIEMIframePanel(horizon.Panel):
    name = _("SIEM Iframe")
    slug = "siem_iframe"
