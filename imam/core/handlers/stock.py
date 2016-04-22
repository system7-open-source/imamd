from __future__ import unicode_literals
from itertools import izip_longest
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import reversion
from unidecode import unidecode
from .base import BaseHandler
from ..forms import InventoryReportForm
from ..models import InventoryLog, Location, StockOutReport, StockReport
from ..utils import chunker
# from messagebox.tasks import send_sms

# DISTRICT_HEAD_CODE = 'DC'
WORDS_PER_REPORT = 3
# DISTRICT_HEAD_POS = Position.get_by_code(DISTRICT_HEAD_CODE)


class StockReportHandler(BaseHandler):
    form_class = InventoryReportForm
    help_text = _(
        'Send {prefix} {keyword} StockCode LastQuantityReceived CurrentTotalStock ... StockCode LastQuantityReceived CurrentTotalStock')
    keyword = 'sto|st0'
    success_text = _(
        'Thank you {name} for sending the stock report for {site_name}')

    def handle(self, text):
        contact = self.msg.connections[0].contact

        if not contact:
            response = _(
                'You are not registered in the system. Please register using the command REG.')
            return self.respond(response)

        parsed = self.parse_message(text)

        sender = contact.worker
        site = parsed.get('site')
        report_data = []

        for report in parsed['reports']:
            form = self.form_class(data=report)

            if form.is_valid():
                report_data.append(form.save())
            else:
                error = form.error()

                if error is None:
                    self.unknown()
                else:
                    self.respond(unidecode(error))
                return

        response = self.process_command(sender, site, report_data)
        self.respond(response)

    def parse_message(self, text):
        parsed = {'reports': []}
        report_fields = ['item_code', 'last_receipt', 'current_stock']
        words = text.upper().split()

        if len(words) % WORDS_PER_REPORT != 0:
            location = Location.get_by_code(words[-1])

            if location:
                words.pop()
                parsed['site'] = location

        # # minimum report length is WORDS_PER_REPORT; other than that,
        # # it's a stock validation request if the length of the command
        # # is 1 (site ID supplied) or less
        # if (len(words) > WORDS_PER_REPORT) or (len(words) <= 1):
        #     location = Location.get_by_code(words[-1])
        #     if location:
        #         words.pop()
        #         parsed['site'] = location

        reports = chunker(words, WORDS_PER_REPORT)
        for report in reports:
            parsed['reports'].append(dict(izip_longest(report_fields, report)))

        return parsed

    def process_command(self, sender, site, report_data):
        if site:
            if not sender.site.is_ancestor_of(site, include_self=True):
                return _('Error in site ID. Please enter or correct the site ID and resend.')
        else:
            site = sender.site

        if not site.is_site:
            return _('Error in site ID. Please enter or correct the site ID and resend.')

        if not report_data:
            # this is a stock validation request, not a stock report
            report = None
            try:
                report = StockReport.objects.filter(site__pk=site.pk).latest()
                response = _(
                    'The site {site_name} reported {stock_list} on date {date}').format(site_name=site.name,
                                                                                        stock_list=report.summary,
                                                                                        date=report.created.strftime(settings.DATETIME_FORMAT))

            except StockReport.DoesNotExist:
                response = _('There are no reports for {site_id}').format(
                    site_id=site.hcid)

            return response

        with reversion.create_revision():
            site_stock_outs = list(StockOutReport.objects.filter(site__pk=site.pk))
            report_items = set()
            exhausted_items = set()
            inventory_logs = []

            for report in report_data:
                report_items.add(report['item'])

                if report['current_stock'] <= 0:
                    exhausted_items.add(report['item'])

                inventory_log = InventoryLog.objects.create(item=report['item'],
                                                            last_quantity_received=report[
                                                                'last_receipt'],
                                                            current_holding=report['current_stock'])
                inventory_logs.append(inventory_log)

            # clear pending stock alerts
            stocked_items = report_items - exhausted_items
            for stock_out in site_stock_outs:
                stock_out.remove(*stocked_items)

            stock_report = StockReport.objects.create(reporter=sender, site=site)
            stock_report.logs.add(*inventory_logs)

            # create stock alerts for exhausted items
            if exhausted_items:
                stock_out = report = StockOutReport.create_stockout_report(site, sender, *exhausted_items)
                # district_heads = site.parent.workers.filter(
                #     position=DISTRICT_HEAD_POS)
                # alert_message = _('Stock outs of {items} were reported at {site_name} with the site ID {site_id} on {date}').format(
                #     items=stock_out.summary, site_name=site.name, site_id=site.hcid, date=stock_out.modified.strftime('%d/%m/%y'))

                # recipients = [dh.mobile for dh in district_heads]
                # send_sms.delay(alert_message, *recipients)
                stock_out.generate_notification()

            # generate or clear any low stock alerts as necessary
            stock_report.check_for_low_stock()

        response = self.success_text.format(
            name=sender.name, site_name=site.name)
        return response
