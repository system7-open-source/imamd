from __future__ import unicode_literals
from calendar import timegm
from rapidsms.models import Connection
from rapidsms.contrib.messagelog.models import Message
from tablib import Dataset

from core.models import Personnel, ProgramReport, StockReport, StockOutReport


def dump_connections():
    print('Running connection dump...')
    dataset = Dataset()
    dataset.headers = ['Identity', 'Backend']

    for connection in Connection.objects.filter(identity__startswith='+'):
        dataset.append([
            connection.identity,
            connection.backend.name
        ])

    with open('connections.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def dump_personnel():
    print('Running worker dump...')
    dataset = Dataset()
    dataset.headers = ['Site ID', 'Name', 'Position', 'Email', 'Mobile']

    for worker in Personnel.objects.all():
        if not worker.mobile.startswith('+'):
            continue

        dataset.append([
            worker.site.hcid,
            worker.name,
            worker.position.code,
            worker.email,
            worker.mobile
        ])

    with open('workers.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def dump_stockouts():
    print('Running stockout dump...')
    dataset = Dataset()
    dataset.headers = ['Site ID', 'Mobile', 'Timestamp', 'Items']

    for stockout in StockOutReport.objects.order_by('created'):
        if not stockout.reporter.mobile.startswith('+'):
            continue

        dataset.append([
            stockout.site.hcid,
            stockout.reporter.mobile,
            timegm(stockout.created.utctimetuple()),
            stockout.summary
        ])

    with open('stockouts.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def dump_stock_reports():
    print('Running stock report dump...')
    dataset = Dataset()
    dataset.headers = ['Site ID', 'Mobile', 'Timestamp', 'Items']

    for stock_report in StockReport.objects.order_by('created'):
        if not stock_report.reporter.mobile.startswith('+'):
            continue

        summary = '; '.join(['{} {} {}'.format(log.item.code, log.last_quantity_received, log.current_holding) for log in stock_report.logs.all()])

        dataset.append([
            stock_report.site.hcid,
            stock_report.reporter.mobile,
            timegm(stock_report.created.utctimetuple()),
            summary
        ])

    with open('stock_reports.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def dump_program_reports():
    print('Running program report dump...')
    dataset = Dataset()
    dataset.headers = ['Site ID', 'Mobile', 'Timestamp', 'Group', 'Program', 'Period code', 'Period number', 'Atot', 'Arel', 'Tin', 'Tout', 'Dead', 'DefT', 'Dcur', 'Dmed']

    for report in ProgramReport.objects.select_related('group', 'program').order_by('created'):
        if not report.reporter.mobile.startswith('+'):
            continue

        dataset.append([
            report.site.hcid,
            report.reporter.mobile,
            timegm(report.created.utctimetuple()),
            report.group.code,
            report.program.code,
            report.period_code,
            report.period_number,
            report.new_marasmic_patients,
            report.readmitted_patients,
            report.patients_transferred_in,
            report.patients_transferred_out,
            report.patient_deaths,
            report.unconfirmed_patient_defaults,
            report.patients_cured,
            report.unresponsive_patients
        ])

    with open('program_reports.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def dump_messages():
    print('Running message dump...')
    dataset = Dataset()
    dataset.headers = ['Connection', 'Backend', 'Direction', 'Timestamp', 'Text']

    for message in Message.objects.all():
        if not message.connection.identity.startswith('+'):
            continue

        dataset.append([
            message.connection.identity,
            message.connection.backend.name,
            message.direction,
            timegm(message.date.utctimetuple()),
            message.text
        ])

    with open('messages.csv', 'w') as f:
        f.write(dataset.csv)

    print('Done')


def run():
    dump_connections()
    dump_messages()
    dump_personnel()
    dump_stockouts()
    dump_stock_reports()
    dump_program_reports()
