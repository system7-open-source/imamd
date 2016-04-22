from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode

from locations.models import Location
from .base import BaseHandler
from ..forms import ItemForm
from ..models import StockOutReport

# from messagebox.tasks import send_sms


# DISTRICT_HEAD_CODE = 'DC'
# DISTRICT_HEAD_POS = Position.get_by_code(DISTRICT_HEAD_CODE)


class StockoutReportHandler(BaseHandler):
    form_class = ItemForm
    help_text = _('To report a stock out, send OUT StockCode')
    keyword = 'out|0ut'
    success_text = _(
        'Thank you. Stock outs of {items} were reported in {site_name} in '
        '{loc} on date {date}.'
    )

    def handle(self, text):
        contact = self.msg.connections[0].contact

        if not contact:
            response = _(
                'You are not registered in the system. Please register using '
                'the command REG.'
            )
            return self.respond(response)

        parsed = self.parse_message(text)

        items = []
        sender = contact.worker
        site = parsed.get('site')

        for code in parsed['item_codes']:
            form = self.form_class(data={'item_code': code})

            if form.is_valid():
                items.append(form.save()['item'])
            else:
                error = form.error()

                if error is None:
                    self.unknown()
                else:
                    self.respond(unidecode(error))
                return
        if not items:
            return

        if site:
            if not sender.site.is_ancestor_of(site, include_self=True):
                response = _(
                    'Error in site ID. Please enter or correct the site ID '
                    'and resend.'
                )
                self.respond(response)
                return
        else:
            site = sender.site

        if not site.is_site:
            response = _(
                'Error in site ID. Please enter or correct the site ID and '
                'resend.'
            )
            self.respond(response)
            return

        report = StockOutReport.create_stockout_report(site, sender, *items)
        report.generate_notification()
        item_code_list = ', '.join(parsed['item_codes'])

        response = self.success_text.format(site_name=site.name,
                                            loc=site.parent.name,
                                            date=report.created.strftime(
                                                '%d/%m/%y'),
                                            items=item_code_list)
        self.respond(unidecode(response))

    def parse_message(self, text):
        parsed = {'item_codes': set()}

        words = text.upper().split()
        if not words:
            return parsed

        location = Location.get_by_code(words[-1])
        if location:
            words.pop()
            parsed['site'] = location

        parsed['item_codes'] = set(words)

        return parsed
