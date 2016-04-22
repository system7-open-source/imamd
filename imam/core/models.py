from __future__ import unicode_literals
from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.timezone import localtime, now, utc
from django.utils.translation import ugettext as _
from django_extensions.db import fields
from rapidsms.models import Contact
import reversion

from messagebox.tasks import send_sms
from utils import iso_week_ends, iso_weeks_in


class Agency(models.Model):
    """Model for site partner NGO agencies"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=8, db_index=True, unique=True)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    def __unicode__(self):
        return self.name


class Item(models.Model):
    """Model class for stocked items"""
    description = models.CharField(max_length=255)
    alt_description = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=8, db_index=True, unique=True)
    alt_code = models.CharField(max_length=8, null=True, blank=True,
                                unique=True)
    unit = models.CharField(max_length=16)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    @classmethod
    def get_by_code(cls, code):
        obj = None

        try:
            obj = cls.objects.get(code__iexact=code)
        except cls.DoesNotExist:
            try:
                obj = cls.objects.get(alt_code__iexact=code)
            except cls.DoesNotExist:
                pass

        return obj

    @classmethod
    def get_by_codes(cls, *codes):
        items = []
        invalid_codes = []

        for code in codes:
            item = cls.get_by_code(code)

            if item is not None:
                items.append(item)
            else:
                invalid_codes.append(code)

        return items, invalid_codes

    def __unicode__(self):
        return self.description


class InventoryLog(models.Model):
    """Model class for individual item transactions. A report will have
    one or more of these"""
    item = models.ForeignKey(Item)
    last_quantity_received = models.IntegerField()
    current_holding = models.IntegerField()
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')


def __unicode__(self):
    return "%s (%i)" % (self.item.description, self.current_holding)


class PatientGroup(models.Model):
    """Model class for patient groups"""
    description = models.CharField(max_length=255)
    code = models.CharField(max_length=8, db_index=True, unique=True)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    @classmethod
    def get_by_code(cls, code):
        obj = None

        try:
            obj = cls.objects.get(code__iexact=code)
        except cls.DoesNotExist:
            pass

        return obj

    def __unicode__(self):
        return self.description


class Position(models.Model):
    """Model class for personnel roles."""
    description = models.CharField(max_length=100)
    alt_description = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(db_index=True, max_length=8, unique=True)
    alt_code = models.CharField(blank=True, null=True, max_length=8,
                                unique=True)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')
    loc_type = models.ForeignKey('locations.LocationType', blank=True,
                                 null=True, related_name='+')

    @classmethod
    def get_by_code(cls, code):
        """Attempts to find the Position instance matching given code"""
        obj = None

        try:
            obj = cls.objects.get(code__iexact=code)
        except cls.DoesNotExist:
            try:
                obj = cls.objects.get(alt_code__iexact=code)
            except cls.DoesNotExist:
                pass

        return obj

    def __unicode__(self):
        return self.description


class ProgramCategory(models.Model):
    """Model class for program categories. For example, the inpatient and
    outpatient programs are both in the Severe Acute Malnutrition category"""
    description = models.CharField(max_length=100)
    acronym = models.CharField(max_length=8, db_index=True, unique=True)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    @classmethod
    def get_by_code(cls, acronym):
        """Attempts to find the matching ProgramCategory instance for the given
        acronym"""
        obj = None

        try:
            obj = cls.objects.get(acronym__iexact=acronym)
        except cls.DoesNotExist:
            pass

        return obj

    def __unicode__(self):
        return "%s (%s)" % (self.description, self.acronym)


class Program(models.Model):
    """Model class for treatment programs"""
    description = models.CharField(max_length=100)
    code = models.CharField(max_length=8, db_index=True, unique=True)
    category = models.ForeignKey(ProgramCategory, related_name='programs')
    sites = models.ManyToManyField('locations.Location',
                                   related_name='site_programs')
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    @classmethod
    def get_by_code(cls, code):
        obj = None

        try:
            obj = cls.objects.get(code__iexact=code)
        except cls.DoesNotExist:
            return obj

        return obj

    def __unicode__(self):
        return "%s (%s)" % (self.description, self.code)

        # def active_site_count(self):
        #     return LocationProgramState.objects.filter(
        #         program__pk=self.pk, current_state__startswith='ACTIVE'
        #     ).count()
        #
        # def inactive_site_count(self):
        #     return LocationProgramState.objects.filter(
        #         program__pk=self.pk, current_state__startswith='INACTIVE'
        #     ).count()
        #
        # def reporting_site_count(self):
        #     return LocationProgramState.objects.filter(
        #         program__pk=self.pk
        #     ).exclude(current_state='OUT').count()
        #
        # def total_site_count(self):
        #     return Location.get_sites().count()


class LocationProgramState(models.Model):
    """Stores information related to a specific program at a given site."""
    LOCATION_STATES = (
        ('OUT', _('Not part of program')),
        ('INACTIVE-TRAINED', _('Trained (but without data)')),
        ('ACTIVE-BAD', _('Active with bad data')),
        ('ACTIVE', _('Active with (some) good data')),
        ('INACTIVE-NEW', _('Recently inactive (8-16 weeks ago)')),
        ('INACTIVE', _('Inactive')),
    )
    site = models.ForeignKey('locations.Location')
    program = models.ForeignKey(Program)
    # TODO: UI for setting training date

    # As for now, there are no critical actions for the program that are
    # related to training date.  It is meant to tell the user who was trained
    # when, which the user can associate with versions of the protocol of
    # service delivery.
    training_date = models.DateTimeField(blank=True, null=True, default=None)
    # Last date of reports coming in, independent on whether this data was
    # accepted or not
    last_report_date = models.DateTimeField(blank=True, null=True, default=None)
    current_state = models.CharField(default='OUT', max_length=20,
                                     choices=LOCATION_STATES)

    class Meta:
        unique_together = (('site', 'program'),)

    def __unicode__(self):
        return "%s, %s: %s" % (
            self.site.name, self.program.code, self.current_state)

    def __setattr__(self, attribute_name, value):
        """Whenever the site and program fields are set (as well as optionally
        training_date and last_report_date), the current_state attribute should
        be (re)computed.

        N.B. this method alone does not ensure the changes are saved to the
        database.
        """
        super(LocationProgramState, self).__setattr__(attribute_name, value)
        if attribute_name in ('program', 'site', 'program_id', 'site_id',
                              'training_date', 'last_report_date'):
            # Make sure the instance has been fully initialised before calling
            # update_current_state().  Testing whether attribute current_state
            # already exists should suffice.
            if hasattr(self, 'current_state'):
                self.update_current_state()

    @classmethod
    def register_data_arrival(cls, program_id, site_id):
        """Update state based on data related to a specific program arriving
        from a specific site.
        """
        spc_instance = \
            cls.objects.get_or_create(site_id=site_id, program_id=program_id)[0]
        # Get current UTC date and time.
        current_dt = now()
        # For the first time that we have data coming in for a site and there
        # is no training date, then we set the training date to the first date
        # for which the data was sent. There are no changes after that training
        # date is set (except possibly by database manager to make a
        # correction).
        if spc_instance.training_date is None:
            spc_instance.training_date = current_dt
        spc_instance.last_report_date = current_dt
        spc_instance.save()

    @classmethod
    def reset_all(cls):
        """This method should:
        * delete all instances of LocationProgramState (i.e. irrespective of
          whether they have any instances of ProgramReport associated with them
          or not)
        * and then do what update_all does
            * with the exception that it should set training_date and
              last_report_date for each instance of LocationProgramState it
              creates, based on creation dates of the instance(s) of
              ProgramReport associated with it
        """
        cls.objects.all().delete()
        site_program_combinations = ProgramReport.objects.values(
            'site', 'program').order_by('site', 'program').distinct()
        for spc in site_program_combinations:
            spc_instance_reports = ProgramReport.objects.filter(
                site=spc['site'], program=spc['program']).order_by('created')
            training_date = spc_instance_reports[0].created
            last_report_date = spc_instance_reports.reverse()[0].created
            lps = cls.objects.create(site_id=spc['site'],
                                     program_id=spc['program'],
                                     training_date=training_date,
                                     last_report_date=last_report_date)
            lps.update_current_state()
            lps.save()

    @classmethod
    def update_all(cls):
        """This method should:
        * create new instances of LocationProgramState for combinations of
          Program and Location (i.e. site) for which instances of ProgramReport
          exist but no instance of LocationProgramState exists and call
          update_current_state() and save() on these newly created instances
        * run update_current_state() and save() for each instance of
          LocationProgramState which has at least one instance of ProgramReport
          associated with it

        This method does not:
        * update current_state of any instance of LocationProgramState which
          does not have any ProgramReport associated with it even if its
          current_state is out of sync with the current combination of its
          training_date, last_report_date and the current date (some LPS may
          have both training_date and last_report_date set but no program
          reports associated with them)
        * update or set last_report_date or training_date even for the
          instances of LocationProgramState it creates
        """
        site_program_combinations = ProgramReport.objects.values(
            'site', 'program').order_by('site', 'program').distinct()
        for spc in site_program_combinations:
            spc_instance = cls.objects.get_or_create(
                site_id=spc['site'], program_id=spc['program'])[0]
            spc_instance.update_current_state()
            spc_instance.save()

    def update_current_state(self):
        """Computes the value of current_state based on relevant instances of
        ProgramReport and/or taking into account current values of training_date
        and last_report_date.

        N.B. this method does not call save() so one must do that explicitly to
        actually store the state update.
        """
        data = ProgramReport.objects.filter(
            program_id=self.program.pk,
            site_id=self.site.pk).order_by('created')
        if data.count() == 0:
            if self.training_date:
                current_time = utc.localize(datetime.utcnow())
                eight_week_bound = current_time - relativedelta(weeks=8)
                if self.last_report_date \
                        and self.last_report_date > eight_week_bound:
                    self.current_state = 'ACTIVE-BAD'
                else:
                    self.current_state = 'INACTIVE-TRAINED'
            else:
                self.current_state = 'OUT'
        else:
            last_report_create_date = data.reverse()[0].created
            current_time = utc.localize(datetime.utcnow())
            eight_week_bound = current_time - relativedelta(weeks=8)
            sixteen_week_bound = current_time - relativedelta(weeks=16)

            if last_report_create_date > eight_week_bound:
                self.current_state = 'ACTIVE'
            elif last_report_create_date > sixteen_week_bound:
                if self.last_report_date \
                        and self.last_report_date > eight_week_bound:
                    self.current_state = 'ACTIVE-BAD'
                else:
                    self.current_state = 'INACTIVE-NEW'
            else:
                if self.last_report_date \
                        and self.last_report_date > eight_week_bound:
                    self.current_state = 'ACTIVE-BAD'
                else:
                    self.current_state = 'INACTIVE'


class Personnel(models.Model):
    """Model class for registered personnel"""
    name = models.CharField(max_length=100, verbose_name='Name')
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    site = models.ForeignKey('locations.Location', related_name='workers',
                             verbose_name='Location')
    position = models.ForeignKey(Position, related_name='+',
                                 verbose_name='Position')
    registered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contact = models.OneToOneField(Contact, related_name='worker', )
    user = models.OneToOneField(User, null=True, related_name='worker',
                                blank=True)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.site.name)

    @property
    def mobile(self):
        return self.contact.default_connection.identity


class Report(models.Model):
    """Abstract base model class for reports"""
    site = models.ForeignKey('locations.Location', verbose_name='Location')
    reporter = models.ForeignKey(
        Personnel, null=True
    )  # NULL indicates report was imported, not submitted via SMS
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()
    created_by = models.ForeignKey(User, blank=True, null=True,
                                   related_name='+')
    last_modified_by = models.ForeignKey(User, blank=True, null=True,
                                         related_name='+')

    class Meta:
        abstract = True
        get_latest_by = 'created'
        ordering = ('-created', '-pk')


class ProgramReport(Report):
    period_number = models.PositiveIntegerField(verbose_name='Report period')
    report_date = models.DateField(verbose_name='period date')
    group = models.ForeignKey(PatientGroup, verbose_name='Group')
    program = models.ForeignKey(Program)
    patients_at_period_start = models.IntegerField(null=True)
    new_marasmic_patients = models.IntegerField(null=True,
                                                verbose_name='New admissions')
    new_oedema_patients = models.IntegerField(null=True)
    new_relapsed_patients = models.IntegerField(null=True)
    hiv_positive_patients = models.IntegerField(null=True)
    readmitted_patients = models.IntegerField(null=True)
    patients_transferred_in = models.IntegerField(null=True,
                                                  verbose_name='Transfers (IN)')
    patients_transferred_out = models.IntegerField(
        null=True, verbose_name='Transfers (OUT)')
    patient_deaths = models.IntegerField(null=True, verbose_name='Deaths')
    confirmed_patient_defaults = models.IntegerField(null=True)
    unconfirmed_patient_defaults = models.IntegerField(null=True,
                                                       verbose_name='Defaults')
    unresponsive_patients = models.IntegerField(null=True,
                                                verbose_name='No response')
    patients_cured = models.IntegerField(null=True, verbose_name='Cured')
    patients_at_period_end = models.IntegerField(null=True)

    class Meta:
        ordering = ('-report_date', '-created', '-pk')

    def __unicode__(self):
        return "%s, %s: %s" % (
            self.site.name, self.program.code, self.report_date)

    @classmethod
    def _validate_period_number(cls, year, value):
        valid_periods = iso_weeks_in(year)
        if 0 < value < valid_periods:
            return True
        return False

    @classmethod
    def _validate_period_spec(cls, period_spec):
        try:
            # originally, the period spec could also start with 'm', but that
            # option has been removed
            if period_spec[0] != 'w':
                return None
            period = int(period_spec[1:])
        except (ValueError, IndexError):
            return None
        if not 0 < period < 53:
            return None
        return 'w', period

    @classmethod
    def get_report(cls, period_spec, group, program, site):
        period_info = cls._validate_period_spec(period_spec)

        if period_info is None:
            return None

        try:
            report = cls.objects.filter(period_number=period_info[1],
                                        group__pk=group.pk,
                                        program__pk=program.pk,
                                        site__pk=site.pk)[0]
        except IndexError:
            return None

        delta = date.today() - report.report_date
        # reports should never be up to a month late
        if abs(delta).days < 31:
            return report
        return None

    @classmethod
    def make_blank_report(cls, period_spec):
        period_info = cls._validate_period_spec(period_spec)

        if period_info is None:
            return None
        return cls(period_number=period_info[1])

    def clean(self):
        try:
            y = self.report_date.year
        except Exception:  # todo: too broad exception clause
            y = self.created.year
        if not self._validate_period_number(y, self.period_number):
            raise ValidationError('Invalid report period')

        return super(ProgramReport, self).clean()

    def save(self, *args, **kwargs):
        if not self.report_date:
            self.report_date = iso_week_ends(self.period_number)

        self.patients_at_period_end = \
            (self.patients_at_period_start or 0) + \
            (self.new_marasmic_patients or 0) + \
            (self.new_oedema_patients or 0) + \
            (self.new_relapsed_patients or 0) + \
            (self.readmitted_patients or 0) + \
            (self.patients_transferred_in or 0) - \
            (self.patients_transferred_out or 0) - \
            (self.patient_deaths or 0) - \
            (
                (self.confirmed_patient_defaults or 0) +
                (self.unconfirmed_patient_defaults or 0)
            ) - \
            (self.patients_cured or 0) - \
            (self.unresponsive_patients or 0)
        return super(ProgramReport, self).save(*args, **kwargs)

    @property
    def period(self):
        return 'w {}'.format(self.period_number)

    @property
    def prior_report(self):
        qs = ProgramReport.objects.filter(period_code=self.period_code,
                                          program__pk=self.program.pk,
                                          group__pk=self.group.pk,
                                          site__pk=self.site.pk)
        obj = None
        try:
            if self.pk is None:
                obj = qs[0]
            else:
                obj = qs.exclude(pk=self.pk)[0]

        except ProgramReport.DoesNotExist:
            pass
        except IndexError:
            pass

        return obj

    def get_prior_reports(self, num):
        qs = ProgramReport.objects.filter(period_code=self.period_code,
                                          program__pk=self.program.pk,
                                          group__pk=self.group.pk,
                                          site__pk=self.site.pk)

        objects = []

        if self.pk is not None:
            qs = qs.exclude(pk=self.pk)

        return objects.extend(qs[:num])

    def summary(self):

        summary = {
            'name': self.reporter.name if self.reporter else '',
            'period_name': 'w {}'.format(self.period_number),
            'SiteName': self.site.name if self.site else '',
            'Atot': (self.new_marasmic_patients or 0) +
                    (self.new_oedema_patients or 0) +
                    (self.new_relapsed_patients or 0),
            'Arel': self.readmitted_patients or 0,
            'Tin': self.patients_transferred_in or 0,
            'Tout': self.patients_transferred_out or 0,
            'Dead': self.patient_deaths or 0,
            'DefT': (self.confirmed_patient_defaults or 0) + (
                self.unconfirmed_patient_defaults or 0),
            'Dcur': self.patients_cured or 0,
            'Dmed': self.unresponsive_patients or 0,
            'End': self.patients_at_period_end or 0,
            'created': self.created,
        }

        if self.pk:
            summary['group_period_name'] = 'w{0[1]} {0[0]}'.format(
                self.report_date.isocalendar())

        return summary


reversion.register(ProgramReport)


class StockOutReport(Report):
    """Model class for stock out reports"""
    items = models.ManyToManyField(Item)

    @classmethod
    @transaction.atomic
    def create_stockout_report(cls, site, reporter, *items):
        try:
            # also clear all low stock alerts for any items in that location
            low_stock_alerts = LowStockAlert.objects.filter(site__pk=site.pk,
                                                            item__in=items)

            for alert in low_stock_alerts:
                alert.delete()

            report = cls.objects.filter(site__pk=site.pk)[0]
            report.reporter = reporter
        except IndexError:
            report = cls(site=site, reporter=reporter)

        report.save()
        report.items.add(*items)

        return report

    @property
    def summary(self):
        return ', '.join(self.items.values_list('code', flat=True))

    def generate_notification(self):
        # we're interested in state and LGA level staff
        location_codes = ['adm1', 'adm2']
        parent_locs = self.site.get_ancestors().filter(
            loc_type__code__in=location_codes)

        alert_message = _(
            'Stock outs of {items} were reported at {site_name} with the site '
            'ID {site_id} on {date}').format(
            items=self.summary, site_name=self.site.name,
            site_id=self.site.hcid, date=self.modified.strftime('%d/%m/%y'))

        phone_numbers = set()

        for loc in parent_locs:
            phone_numbers.update(
                [worker.mobile for worker in loc.workers.all()])

        # if the alert is received after 8.00AM and before 8.00PM, dispatch
        # immediately, else schedule for the next day
        current_timestamp = localtime(now())
        lower_timestamp_bound = current_timestamp.replace(hour=8, minute=0,
                                                          second=0,
                                                          microsecond=0)
        upper_timestamp_bound = current_timestamp.replace(hour=20, minute=0,
                                                          second=0,
                                                          microsecond=0)

        args = list()
        args.append(alert_message)
        args.extend(phone_numbers)

        if lower_timestamp_bound <= current_timestamp <= upper_timestamp_bound:
            send_sms.delay(*args)
        elif current_timestamp > upper_timestamp_bound:
            dispatch_timestamp = lower_timestamp_bound + timedelta(days=1)
            send_sms.apply_async(args=args, eta=dispatch_timestamp)
        else:
            dispatch_timestamp = lower_timestamp_bound
            send_sms.apply_async(args=args, eta=dispatch_timestamp)

    @transaction.atomic
    def remove(self, *items):
        self.items.remove(*items)

        if not self.items.exists():
            self.delete()


class StockReport(Report):
    logs = models.ManyToManyField(InventoryLog)

    @property
    def summary(self):
        logs = ', '.join(
            ['{}: {}'.format(log.item.code, log.current_holding) for log in
             self.logs.all()])

        return logs

    @property
    def dump(self):
        logs = []

        for log in self.logs.all():
            logs.append({
                'item': log.item.code,
                'received': log.last_quantity_received,
                'holding': log.current_holding
            })

        return logs

    @transaction.atomic
    def check_for_low_stock(self):
        item = Item.get_by_code('RUTF')
        rutf_logs = self.logs.filter(item__code=item.code)

        for log in rutf_logs:
            minimum_stock = get_total_minimum_rutf_stock(self.site)
            if (log.current_holding <= minimum_stock) and (minimum_stock > 0):
                # generate low stock alert if no existing low stock or stock
                # alerts exist
                stockout = None
                try:
                    stockout = StockOutReport.objects.get(site__pk=self.site.pk)
                except StockOutReport.DoesNotExist:
                    pass

                # if a stock out alert exists for the specified item, don't
                # bother creating a low stock alert
                if stockout and stockout.items.filter(code=item.code).exists():
                    continue

                alert, newobj = LowStockAlert.objects.get_or_create(
                    site=self.site,
                    item=item
                )
                alert.created = self.created
                alert.save()
            elif log.current_holding >= minimum_stock:
                # clear any existing low stock alerts
                alert = None
                try:
                    alert = LowStockAlert.objects.get(site=self.site, item=item)
                except LowStockAlert.DoesNotExist:
                    pass

                if alert:
                    alert.delete()


class LowStockAlert(models.Model):
    site = models.ForeignKey('locations.Location')
    item = models.ForeignKey(Item)
    created = fields.CreationDateTimeField()
    modified = fields.ModificationDateTimeField()

    def __unicode__(self):
        return "%s: %s (%s)" % (self.site.name, self.item.code, self.created)

    def generate_notification(self):
        # we're interested in state and LGA level staff
        location_codes = ['adm1', 'adm2']
        parent_locs = self.site.get_ancestors().filter(
            loc_type__code__in=location_codes)

        alert_message = _(
            'The site {site_name} with the site ID {site_id} reported low '
            'stock of {item} on {date}').format(
            site_name=self.site.name, site_id=self.site.hcid,
            date=self.modified.strftime('%d/%m/%y'), item=self.item.code)

        phone_numbers = set()

        for loc in parent_locs:
            phone_numbers.update(
                [worker.mobile for worker in loc.workers.all()])

        # if the alert is received after 8.00AM and before 8.00PM, dispatch
        # immediately, else schedule for the next day
        current_timestamp = localtime(now())
        lower_timestamp_bound = current_timestamp.replace(hour=8, minute=0,
                                                          second=0,
                                                          microsecond=0)
        upper_timestamp_bound = current_timestamp.replace(hour=20, minute=0,
                                                          second=0,
                                                          microsecond=0)

        args = list()
        args.append(alert_message)
        args.extend(phone_numbers)

        if lower_timestamp_bound <= current_timestamp <= upper_timestamp_bound:
            send_sms.delay(*args)
        elif current_timestamp > upper_timestamp_bound:
            dispatch_timestamp = lower_timestamp_bound + timedelta(days=1)
            send_sms.apply_async(args=args, eta=dispatch_timestamp)
        else:
            dispatch_timestamp = lower_timestamp_bound
            send_sms.apply_async(args=args, eta=dispatch_timestamp)


def get_minimum_rutf_stock(site, program, group):
    # retrieve last four of the five most recent reports
    qs = ProgramReport.objects.filter(site__pk=site.pk,
                                      program__pk=program.pk,
                                      group__pk=group.pk)[1:5]

    if qs.count() == 0:
        return 0.0

    multiplier = 1.5

    atots = []

    for report in qs:
        atots.append(report.summary()['Atot'])

    caseload = abs(sum(atots) / float(len(atots)))
    minimum_stock = caseload * multiplier

    return minimum_stock


def get_total_minimum_rutf_stock(site):
    groups = PatientGroup.objects.exclude(code='05')
    programs = Program.objects.exclude(code='SFP')

    total_minimum = 0.0

    for group in groups:
        for program in programs:
            total_minimum += get_minimum_rutf_stock(site, program, group)

    return total_minimum
