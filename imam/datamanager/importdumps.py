from __future__ import unicode_literals
import csv
from datetime import datetime
from django.utils.timezone import utc
from rapidsms.models import Backend, Connection, Contact
from rapidsms.contrib.messagelog.models import Message

from locations.models import Location
from core.models import Item, InventoryLog, PatientGroup, Personnel, Position, Program, ProgramReport, StockOutReport, StockReport


def import_connection_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            backend = Backend.objects.get(name__iexact=row['Backend'])
            Connection.objects.create(identity=row['Identity'], backend=backend)

    print('Done')


def import_personnel_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            connection = Connection.objects.get(identity=row['Mobile'])
            if not connection.contact:
                contact = Contact.objects.create(name=row['Name'])
                connection.contact = contact
                connection.save()

            site = Location.get_by_code(row['Site ID'])
            if not site:
                print(row)
                continue

            position = Position.get_by_code(row['Position'])
            email = row['Email'] or None

            Personnel.objects.create(
                name=row['Name'],
                position=position,
                email=email,
                site=site,
                contact=contact
            )

    print('Done')


def import_stockout_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            site = Location.get_by_code(row['Site ID'])
            reporter = Connection.objects.get(identity=row['Mobile']).contact.worker
            created = utc.localize(datetime.utcfromtimestamp(int(row['Timestamp'])))
            modified = created

            stockout = StockOutReport.objects.create(site=site,
                reporter=reporter, created=created, modified=modified)

            items = []
            for item_code in row['Items'].split(','):
                items.append(Item.get_by_code(item_code.strip()))

            stockout.items.add(*items)

    print('Done')


def import_program_report_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            site = Location.get_by_code(row['Site ID'])

            if not site:
                print(row)
                continue

            reporter = Connection.objects.get(identity=row['Mobile']).contact.worker
            created = utc.localize(datetime.utcfromtimestamp(int(row['Timestamp'])))
            modified = created
            group = PatientGroup.get_by_code(row['Group'])
            program = Program.get_by_code(row['Program'])
            period_code = row['Period code']
            period_number = row['Period number']
            atot = int(row['Atot'])
            tin = int(row['Tin'])
            tout = int(row['Tout'])
            dead = int(row['Dead'])
            deft = int(row['DefT'])
            dcur = int(row['Dcur'])
            dmed = int(row['Dmed'])

            ProgramReport.objects.create(site=site,
                reporter=reporter,
                created=created,
                modified=modified,
                group=group,
                program=program,
                period_number=period_number,
                period_code=period_code,
                new_marasmic_patients=atot,
                patients_transferred_in=tin,
                patients_transferred_out=tout,
                patient_deaths=dead,
                unconfirmed_patient_defaults=deft,
                patients_cured=dcur,
                unresponsive_patients=dmed)

    print('Done')


def import_message_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            connection = Connection.objects.get(identity=row['Connection'])
            direction = row['Direction']
            timestamp = utc.localize(datetime.utcfromtimestamp(int(row['Timestamp'])))
            text = row['Text']

            Message.objects.create(connection=connection,
                direction=direction, date=timestamp,
                text=text)
    
    print('Done')


def import_stock_report_dump(sourcefile):
    with open(sourcefile) as f:
        reader = csv.DictReader(f)

        for row in reader:
            site = Location.get_by_code(row['Site ID'])

            if not site:
                print(row)
                continue

            reporter = Connection.objects.get(identity=row['Mobile']).contact.worker
            created = utc.localize(datetime.utcfromtimestamp(int(row['Timestamp'])))
            logs = []
            for chunk in row['Items'].split(';'):
                bits = chunk.split()
                item = Item.get_by_code(bits[0])
                received = int(bits[1])
                holding = int(bits[2])
            
                logs.append(InventoryLog.objects.create(item=item,
                    last_quantity_received=received,
                    current_holding=holding))

            report = StockReport.objects.create(site=site, reporter=reporter,
                created=created)
            report.logs.add(*logs)

    print('Done')
