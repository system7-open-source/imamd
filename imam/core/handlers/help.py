from __future__ import unicode_literals
import re
from django.utils.translation import ugettext_lazy as _
# from locations.models import Location
from .base import BaseHandler
from .admissions import AdmissionValidationHandler
from .ipf import IPFReportHandler
from .otp import OTPReportHandler
from .registration import RegistrationHandler
from .sfp import SFPReportHandler
from .stock import StockReportHandler
from .stockout import StockoutReportHandler

handlers = [
    AdmissionValidationHandler,
    IPFReportHandler,
    OTPReportHandler,
    RegistrationHandler,
    SFPReportHandler,
    StockoutReportHandler,
    StockReportHandler,
]

site_id_pat = re.compile(r'^\s*siteid\s*$', re.I)


class HelpHandler(BaseHandler):
    keyword = 'help'
    help_text = _('Send {prefix} {keyword} *COMMAND* or *COMMAND* to get help on COMMAND')

    def handle(self, message):
        for handler in handlers:
            match = handler._keyword().match('{} {}'.format(self.prefix, message))

            if match:
                if handler.help_text:
                    return self.respond(handler.help_text.format(prefix=handler.prefix, keyword=handler.keyword.split('|')[0]))

        if site_id_pat.match(message):
            contact = self.msg.connections[0].contact
            if contact:
                worker = contact.worker
                response = _('Hello {name}, you are registered at {site_name} with site ID {site_id}').format(
                        name=worker.name, site_name=worker.site.name, site_id=worker.site.hcid
                )
            else:
                response = _('You are not registered in the system. Please register using the command REG.')
        else:
            response = _('The SMS is not clear. Please review format and send again.')

        self.respond(response)
