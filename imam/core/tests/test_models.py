__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'

import dateutil.tz
import dateutil.relativedelta
import datetime

import mock
from model_mommy import mommy

import django.db
import django.utils.timezone
import django.test
import django.forms.models

import core.models
import locations.models


class LocationProgramStateTest(django.test.TestCase):
    def test_class_can_be_imported(self):
        class_name = 'LocationProgramState'
        self.assertTrue(hasattr(core.models, class_name),
                        'Class %s not found in core.models.' % class_name)

    def test_class_can_be_instantiated(self):
        self.assertIsInstance(core.models.LocationProgramState(),
                              core.models.LocationProgramState)

    def test_default_field_values(self):
        lps0 = core.models.LocationProgramState()
        self.assertEqual(lps0.current_state, 'OUT')
        self.assertEqual(lps0.last_report_date, None)
        self.assertEqual(lps0.program_id, None)
        self.assertEqual(lps0.site_id, None)
        self.assertEqual(lps0.training_date, None)

    def test_default_current_state_is_a_valid_state(self):
        # Define a container with all valid values for current_state.
        valid_state_values = zip(
            *core.models.LocationProgramState.LOCATION_STATES)[0]
        # Test if the default value of the current_state attribute is a valid
        # state.
        lps0 = core.models.LocationProgramState()
        self.assertIn(lps0.current_state, valid_state_values)

    def test_register_data_arrival_uses_offset_aware_datetimes(self):
        """There was an error in the code which caused register_data_arrival()
        to fail throwing a TypeError exception.  This test is to demonstrate it
        and prevent regressions.
        """
        # Mock method LocationProgramState.save() before calling method
        # LocationProgramState.register_data_arrival().
        with mock.patch.object(
                core.models.LocationProgramState,
                'save', autospec=True) as mock_save:
            p0 = mommy.make(core.models.Program)
            l0 = mommy.make(locations.models.Location)
            core.models.LocationProgramState.register_data_arrival(
                program_id=p0.pk, site_id=l0.pk
            )
        # Make sure that the mocked save function has been called at least once.
        # If it has not then it may be time to modify this test.
        self.assertGreater(mock_save.call_count, 0)
        # Get the self argument sent to method save() by register_data_arrival()
        internal_lps_object = mock_save.call_args_list[0][0][0]
        training_date = internal_lps_object.training_date
        last_report_date = internal_lps_object.last_report_date
        current_time = django.utils.timezone.now()
        try:
            current_time > training_date
        except TypeError as e:
            self.fail(
                'Attribute LocationProgramState.training_date computed in '
                'LocationProgramState.register_data_arrival() is offset-naive '
                'while it should be offset-aware. Exception: %s' % e.message)
        try:
            current_time > last_report_date
        except TypeError as e:
            self.fail(
                'Attribute LocationProgramState.last_report_date computed in '
                'LocationProgramState.register_data_arrival() is offset-naive '
                'while it should be offset-aware. Exception: %s' % e.message)

    def test_new_objects_set_up_correctly_on_register_data_arrival(self):
        # Test for three consecutive data arrival events - one per object.
        for i in xrange(3):
            current_number_of_lps_objects = len(
                core.models.LocationProgramState.objects.all())
            self.assertEquals(current_number_of_lps_objects, i,
                              'Current number of LocationProgramState objects '
                              'should be zero at this point.')
            l0 = mommy.make(locations.models.Location)
            p0 = mommy.make(core.models.Program)
            # Call register_data_arrival using a mock date.
            with mock.patch('core.models.now') as mock_now:
                fake_dt = datetime.datetime(1, 1, 1, 0, 0, i,
                                            tzinfo=dateutil.tz.tzutc())
                mock_now.return_value = fake_dt
                core.models.LocationProgramState.register_data_arrival(
                    program_id=p0.pk, site_id=l0.pk
                )
            # Make sure that the mocked now() function has been called at least
            # once.  If it has not then it may be time to modify this test.
            self.assertGreater(mock_now.call_count, 0)

            current_number_of_lps_objects = len(
                core.models.LocationProgramState.objects.all())
            self.assertEquals(current_number_of_lps_objects, i + 1,
                              'It seems that the LocationProgramState object '
                              'has not been created or saved.')
            # Get the newly created object.
            lps0 = core.models.LocationProgramState.objects.get(site=l0,
                                                                program=p0)
            # Check if program and site are set correctly.
            self.assertEqual(lps0.program, p0)
            self.assertEqual(lps0.site, l0)
            # Check if the dates are set correctly to our fake now().
            localised_fake_dt = django.utils.timezone.localtime(fake_dt)
            self.assertEqual(lps0.training_date, localised_fake_dt)
            self.assertEqual(lps0.last_report_date, localised_fake_dt)

    def test_existing_objects_updated_correctly_on_register_data_arrival(self):
        # Prepare objects.
        p0 = mommy.make(core.models.Program)
        sites = mommy.make(locations.models.Location, _quantity=3)
        for site in sites:
            mommy.make(core.models.LocationProgramState, site=site, program=p0)
        # Test for six consecutive data arrival events - two for each of the
        # three objects.
        for j in [1, 10]:  # initial events for all objects when j=1
            # Test each of the three objects.
            for i in xrange(3):
                lps_i = core.models.LocationProgramState.objects.get(
                    site=sites[i])
                # Attribute training_date should be None before method
                # register_data_arrival is called the first time.
                if j == 1:
                    self.assertIs(lps_i.training_date, None)
                # Call register_data_arrival using a mock date.
                with mock.patch('core.models.now') as mock_now:
                    fake_dt = datetime.datetime(
                        1, 1, 1, 0, 0, i * j, tzinfo=dateutil.tz.tzutc())
                    mock_now.return_value = fake_dt
                    site = lps_i.site
                    program = lps_i.program
                    self.assertEqual(program, p0)
                    self.assertIn(site, sites)
                    core.models.LocationProgramState.register_data_arrival(
                        program_id=program.pk, site_id=site.pk
                    )
                # Make sure that the mocked now() function has been called at
                # least once.  If it has not then it may be time to modify this
                # test.
                self.assertGreater(mock_now.call_count, 0)

                current_number_of_lps_objects = len(
                    core.models.LocationProgramState.objects.all())
                self.assertEquals(
                    current_number_of_lps_objects, 3,
                    'There should be exactly 3 LocationProgramState objects in '
                    'the database at this point.  '
                    'There are %d' % current_number_of_lps_objects)
                # Get the object associated with the current value of site.
                lps0 = core.models.LocationProgramState.objects.get(
                    site=site, program=program)
                # Check if program and site are set correctly.
                self.assertEqual(lps0.program, p0)
                self.assertEqual(lps0.site, site)
                # Check if the dates are set correctly to our fake dates.
                # Both dates should be the same after the first event and differ
                # after the second event as training_date is not supposed to be
                # modified by the tested function when it is not set to None.
                fake_training_date = datetime.datetime(
                    1, 1, 1, 0, 0, i, tzinfo=dateutil.tz.tzutc())
                localised_fake_training_date = \
                    django.utils.timezone.localtime(fake_training_date)
                localised_fake_last_report_date = \
                    django.utils.timezone.localtime(fake_dt)
                self.assertEqual(lps0.training_date,
                                 localised_fake_training_date)
                self.assertEqual(lps0.last_report_date,
                                 localised_fake_last_report_date)

    def test_reset_all_deletes_all_lps_objects_when_no_pr_objects_exist(self):
        """If there are no ProgramReport objects in the system, all objects of
        class LocationProgramState are deleted and no new objects of that class
        are left in the system after LocationProgramState.reset_all() runs.
        """
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 0)
        # Create three LocationProgramState objects and confirm their count.
        mommy.make(core.models.LocationProgramState, _quantity=3)
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 3)
        # There should be no ProgramReport objects at this point.
        current_number_of_pr_objects = \
            core.models.ProgramReport.objects.all().count()
        self.assertEqual(current_number_of_pr_objects, 0)
        # With no ProgramReport objects all LocationProgramState objects should
        # be deleted upon reset_all().
        core.models.LocationProgramState.reset_all()
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 0)

    def test_reset_all_deletes_all_lps_objects_for_which_no_pr_object_exist(
            self):
        """All objects of class LocationProgramState not related by site AND
        program to any of the existing ProgramReport objects are purged from the
        system after LocationProgramState.reset_all() completes.
        """
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 0)
        # Create three LocationProgramState objects and confirm their count.
        mommy.make(core.models.LocationProgramState, _quantity=3)
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 3)
        # There should be no ProgramReport objects at this point.
        current_number_of_pr_objects = \
            core.models.ProgramReport.objects.all().count()
        self.assertEqual(current_number_of_pr_objects, 0)
        # Create one ProgramReport object.
        pr0 = mommy.make(core.models.ProgramReport)
        current_number_of_pr_objects = \
            core.models.ProgramReport.objects.all().count()
        self.assertEqual(current_number_of_pr_objects, 1)
        # Create a LocationProgramState object for Program and Site taken from
        # the ProgramReport object just created.
        program = pr0.program
        site = pr0.site
        lps0 = mommy.make(core.models.LocationProgramState, program=program,
                          site=site)
        # Both dates in the newly created objects should be set to None.
        self.assertIsNone(lps0.training_date)
        self.assertIsNone(lps0.last_report_date)
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 4)

        # With only one ProgramReport object, only one LocationProgramState
        # object - the one related to the ProgramReport object by the values of
        # site and program - should exist in the system after reset_all()
        # completes.
        core.models.LocationProgramState.reset_all()
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 1)
        recreated_lps = core.models.LocationProgramState.objects.first()
        # The newly recreated object should not be the same as the old one.
        self.assertIsNot(lps0, recreated_lps)
        self.assertNotEqual(lps0, recreated_lps)
        # Both site and program associated with it should be the same as they
        # were in case of the old object.
        self.assertEqual(lps0.site_id, recreated_lps.site_id)
        self.assertEqual(lps0.program_id, recreated_lps.program_id)
        # The dates in the recreated object should no longer be set to None.
        self.assertIsNotNone(recreated_lps.training_date)
        self.assertIsNotNone(recreated_lps.last_report_date)

    def test_reset_all_makes_one_lps_for_each_site_program_combination(self):
        """Exactly one LocationProgramState object should be created per each
        program-site combination found in existing ProgramReport objects.
        """
        # Create one LocationProgramState object.
        lps_without_pr = mommy.make(core.models.LocationProgramState)
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 1)

        # Prepare ProgramReport objects for tested combinations of Program and
        # Site.
        programs = mommy.make(core.models.Program, _quantity=3)
        sites = mommy.make(locations.models.Location, _quantity=3)
        number_of_unique_combinations = 0
        prs_per_combination = 4
        recorded_combinations = []
        for s in sites:
            for p in programs:
                mommy.make(core.models.ProgramReport,
                           _quantity=prs_per_combination,
                           program=p, site=s)
                recorded_combinations.append({'program': p, 'site': s})
                number_of_unique_combinations += 1
        current_number_of_reports = \
            core.models.ProgramReport.objects.all().count()
        self.assertEqual(current_number_of_reports,
                         prs_per_combination * number_of_unique_combinations)
        # There should still exist only one LocationProgramState object at this
        # stage.
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects, 1)
        # Call reset_all() and see if the following happens:
        #  - The old LocationProgramState object should disappear.
        #  - A number of objects of that class equal to the number of unique
        #    combinations tested should have been created.
        core.models.LocationProgramState.reset_all()
        number_of_objects_without_pr = \
            core.models.LocationProgramState.objects.filter(
                site=lps_without_pr.site).count()
        self.assertEqual(number_of_objects_without_pr, 0)
        current_number_of_lps_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(current_number_of_lps_objects,
                         number_of_unique_combinations)
        # A LocationProgramState object for each unique combination should be
        # found in the system.
        for c in recorded_combinations:
            number_found = core.models.LocationProgramState.objects.filter(
                program=c['program'], site=c['site']
            ).count()
            self.assertEqual(
                number_found, 1,
                'Found %d LocationProgramState objects for this program-site '
                'combination.  There should be just 1.' % number_found
            )

    def test_reset_all_sets_dates_on_newly_created_objects_correctly(self):
        """LocationProgramState.training_date should be the creation date of
        the oldest ProgramReport object for a particular program-site
        combination.
        LocationProgramState.last_report_date should be the creation date
        of the newest ProgramReport object for a particular program-site
        combination.
        """
        programs = mommy.make(core.models.Program, _quantity=2)
        sites = mommy.make(locations.models.Location, _quantity=2)
        combinations = []
        for pi in xrange(2):
            si = pi ^ 1
            combination_key = '%d%d' % (pi, si)
            prs = mommy.make(
                core.models.ProgramReport, _quantity=3,
                program=programs[pi], site=sites[si])
            dates = [pr.created for pr in prs]
            dates.sort()
            combinations.append(
                {'combination': combination_key, 'prs': prs, 'dates': dates}
            )
        core.models.LocationProgramState.reset_all()
        # Check if dates were set correctly.
        for c in combinations:
            program = c['prs'][0].program
            site = c['prs'][0].site
            first_date = c['dates'][0]
            latest_date = c['dates'][-1]
            lpss = core.models.LocationProgramState.objects.filter(
                site=site, program=program
            )
            number_found_for_this_combination = lpss.count()
            self.assertEqual(
                number_found_for_this_combination, 1,
                'Found %d LocationProgramState objects for this program-site '
                'combination.  There should be just 1.' %
                number_found_for_this_combination
            )
            lps = lpss[0]
            # LocationProgramState.training_date should be the creation date of
            # the oldest ProgramReport object for a particular program-site
            # combination.
            self.assertEqual(lps.training_date, first_date)
            # LocationProgramState.last_report_date should be the creation date
            # of the newest ProgramReport object for a particular program-site
            # combination.
            self.assertEqual(lps.last_report_date, latest_date)

    def test_reset_all_does_not_change_any_program_report(self):
        # Create a number of test objects of class ProgramReport and store their
        # values in a separate data structure.
        prs0 = mommy.make(core.models.ProgramReport, _quantity=3)
        dicts0 = [django.forms.models.model_to_dict(pr) for pr in prs0]
        # Run the method under test.
        core.models.LocationProgramState.reset_all()
        # Acquire values of ProgramReport objects stored in the system after
        # the method has been run.
        prs1 = core.models.ProgramReport.objects.all()
        dicts1 = [django.forms.models.model_to_dict(pr) for pr in prs1]
        # The total number of ProgramReport objects should remain unchanged.
        number_of_prs_before = len(dicts0)
        number_of_prs_after = len(dicts1)
        self.assertEqual(number_of_prs_before, number_of_prs_after)
        # Values of all ProgramReport objects should remain unchanged.
        i = 0
        while i < number_of_prs_before:
            self.assertIn(dicts0[i], dicts1,
                          'The %dth of the original ProgramReport objects '
                          'checked did not match any of the ProgramReport '
                          'objects after method reset_all() has been run which '
                          'suggests that the method may have an unwanted side '
                          'effect.' % (i + 1))
            i += 1

    def test_reset_all_calls_current_state_updater_for_all_instances(
            self):
        """The method which takes care of updating the current_state attribute
        of LocationProgramState objects should be called by reset_all() for
        each of the objects of class LocationProgramState it creates in order
        to make sure that current_state is up to date.
        """
        # Test on LocationProgramState objects each associated with at least one
        # instance of the ProgramReport class.
        mommy.make(core.models.ProgramReport, _quantity=5)
        self._check_current_state_updater_called_for_all_instances(
            class_method=core.models.LocationProgramState.reset_all)

    def _serialise_instances(self):
        """Return a list of instances turned into dictionaries."""
        result = core.models.LocationProgramState.objects.all()
        result_serialised = [
            django.forms.models.model_to_dict(lps)
            for lps in result
        ]
        return result_serialised

    def test_update_all_does_not_delete_nor_unnecessarily_change_any_instances(
            self):
        """Method update_all() should not delete existing instances."""
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 0)

        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 0)

        # Add some instances not associated with any program report.
        mommy.make(core.models.LocationProgramState, _quantity=3)
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 3)
        before = self._serialise_instances()

        # Check if update_all() does not delete or change existing instances.
        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 3)
        after = self._serialise_instances()
        for o in before:
            self.assertIn(o, after)

        # Create some instance of ProgramReport.
        before = self._serialise_instances()
        mommy.make(core.models.ProgramReport, _quantity=3)
        # Run update_all() to check if it creates three new instances without
        # deleting any of the old instances.
        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 6)
        after = self._serialise_instances()
        for o in before:
            self.assertIn(o, after)

    def test_update_all_creates_missing_instances(self):
        """Method update_all() should create new instances of
        LocationProgramState for combinations of Program and Location (i.e.
        site) for which instances of ProgramReport exist but no instance of
        LocationProgramState exists.
        """
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 0)
        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 0)
        mommy.make(core.models.ProgramReport, _quantity=3)
        self.assertEqual(number_of_instances, 0)
        # Run update_all() to check if it creates three new instances.
        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(
            number_of_instances, 3, 'New instances for all of the existing '
                                    'ProgramReport objects should have been '
                                    'created (one per object). [STEP 1]')
        # Add some instances not associated with any program report.
        mommy.make(core.models.LocationProgramState, _quantity=3)
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 6)
        # Add some new program reports and make sure that the current number of
        # instances is still correct.
        mommy.make(core.models.ProgramReport, _quantity=3)
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_instances, 6)
        # Run update_all() and see if it creates three new instances (one per
        # each of the newly created ProgramReport objects) and does not delete
        # any of the old ones.
        core.models.LocationProgramState.update_all()
        number_of_instances = \
            core.models.LocationProgramState.objects.all().count()
        # There should be exactly nine instances in the system at this point.
        self.assertEqual(
            number_of_instances, 9, 'New instances for all of the existing '
                                    'ProgramReport objects should have been '
                                    'created (one per object). [STEP 2]')

    def test_update_all_may_only_modify_current_state_of_instances(self):
        """Method update_all() should not change any part of the existing
         LocationProgramState object including the current_state attribute if
         the attribute is up to date (as defined in update_current_state()).
         Even if the attribute is not up to date, no other attributes can be
         changed.
        """
        prs = mommy.make(core.models.ProgramReport, _quantity=3)
        for pr in prs:
            mommy.make(core.models.LocationProgramState,
                       program=pr.program, site=pr.site)
        originals = core.models.LocationProgramState.objects.all()
        originals_serialised = [
            django.forms.models.model_to_dict(lps, exclude='current_state')
            for lps in originals
        ]
        core.models.LocationProgramState.update_all()
        afterwards = core.models.LocationProgramState.objects.all()
        afterwards_serialised = [
            django.forms.models.model_to_dict(lps, exclude='current_state')
            for lps in afterwards
        ]
        for o in originals_serialised:
            self.assertIn(o, afterwards_serialised)

    def _check_current_state_updater_called_for_all_instances(
            self, class_method, error_message_prefix=''):
        # Mock method LocationProgramState.update_current_state() before calling
        # the given class method of LocationProgramState.
        with mock.patch.object(
                core.models.LocationProgramState, 'update_current_state',
                autospec=True
        ) as mock_ucs:
            class_method()
        # Make sure that the mocked method has been called at least once for
        # each of the existing instances.
        lpss = core.models.LocationProgramState.objects.all()
        calls = []
        for lps in lpss:
            calls.append(mock.call(lps))
        try:
            mock_ucs.assert_has_calls(calls, any_order=True)
        except AssertionError as e:
            self.fail(error_message_prefix +
                      'Method %s() has not run the current state '
                      'updater method on all existing LocationProgramState '
                      'objects.  Original error message: %s' % (
                          class_method.__name__, e))

    def _check_current_state_updater_not_called_for_any_instance(
            self, error_message_prefix=''):
        # Mock method LocationProgramState.update_current_state() before calling
        # method LocationProgramState.update_all().
        with mock.patch.object(
                core.models.LocationProgramState, 'update_current_state',
                autospec=True
        ) as mock_ucs:
            core.models.LocationProgramState.update_all()
        # Make sure that the mocked method has not been called even once for
        # any of the existing instances.
        self.assertEqual(
            mock_ucs.call_count, 0,
            error_message_prefix + 'Method update_all() has run the current '
                                   'state updater method on at least one of the'
                                   ' existing LocationProgramState objects it '
                                   'should not run it on.')

    def test_update_all_only_calls_current_state_updater_for_instances_with_pr(
            self):
        """The method which takes care of updating the current_state attribute
        of LocationProgramState objects should be called by update_all() for
        each stored object of class LocationProgramState for which at least one
        associated ProgramReport object exists in order to make sure that
        current_state is up to date.  The method should not be called for
        instances for which no associated ProgramReport object exists.
        """
        # Test on LocationProgramState objects each associated with at least one
        # instance of the ProgramReport class.
        prs = mommy.make(core.models.ProgramReport, _quantity=5)
        for pr in prs:
            mommy.make(core.models.LocationProgramState, program=pr.program,
                       site=pr.site)
        self._check_current_state_updater_called_for_all_instances(
            class_method=core.models.LocationProgramState.update_all,
            error_message_prefix='(Tested for instances with associated '
                                 'ProgramReport objects) ')
        core.models.LocationProgramState.objects.all().delete()
        core.models.ProgramReport.objects.all().delete()
        # Test on LocationProgramState objects with no associated instances of
        # the ProgramReport class.
        mommy.make(core.models.LocationProgramState, _quantity=5)
        self._check_current_state_updater_not_called_for_any_instance(
            error_message_prefix='(Tested for instances WITHOUT associated '
                                 'ProgramReport objects) ')
        core.models.LocationProgramState.objects.all().delete()

    def _current_state_date_with_delta(self, weeks_ago=0):
        delta = dateutil.relativedelta.relativedelta(weeks=weeks_ago)
        now = django.utils.timezone.localtime(django.utils.timezone.now())
        return now - delta

    def _set_current_state_to_different_than_given(self, lps, state_to_avoid):
        # Ensure that current_state is not already set to the value we test for.
        if lps.current_state == state_to_avoid:
            if state_to_avoid != 'OUT':
                lps.current_state = 'OUT'
            else:
                lps.current_state = 'ACTIVE'

    def test_current_state_set_correctly_for_instances_with_no_program_reports(
            self):
        """Test instances of LocationProgramState for which there are not any
        associated ProgramReport objects in the system.
        """
        now = self._current_state_date_with_delta()
        eight_week_bound = self._current_state_date_with_delta(weeks_ago=8)
        # if there are no program reports
            # if any training date exist
                # if last report date exists and newer than 8 weeks
        lps_fresh_dates = mommy.make(core.models.LocationProgramState,
                                     training_date=now, last_report_date=now)
        # Ensure that current_state is not already set to the value we test for.
        lps_fresh_dates.current_state = 'OUT'
                    # ACTIVE-BAD
        lps_fresh_dates.update_current_state()
        self.assertEqual(lps_fresh_dates.current_state, 'ACTIVE-BAD')
                # else (i.e. date does not exist or older than 8 weeks)
        lps_no_last_report = mommy.make(core.models.LocationProgramState,
                                        training_date=now)
        lps_8_week_old = mommy.make(core.models.LocationProgramState,
                                    training_date=now,
                                    last_report_date=eight_week_bound)
        # Ensure that current_state is not already set to the value we test for.
        lps_no_last_report.current_state = 'OUT'
        lps_8_week_old.current_state = 'OUT'
                     # INACTIVE-TRAINED
        lps_no_last_report.update_current_state()
        self.assertEqual(lps_no_last_report.current_state, 'INACTIVE-TRAINED')
        lps_8_week_old.update_current_state()
        self.assertEqual(lps_8_week_old.current_state, 'INACTIVE-TRAINED')
            # else (i.e. training date does not exist)
        lps_no_training_date = mommy.make(core.models.LocationProgramState)
        lps_fresh_last_report_and_no_training_date = mommy.make(
            core.models.LocationProgramState, last_report_date=now)
        # Ensure that current_state is not already set to the value we test for.
        lps_no_training_date.current_state = 'ACTIVE'
        lps_fresh_last_report_and_no_training_date.current_state = 'ACTIVE'
                # OUT
        lps_no_training_date.update_current_state()
        self.assertEqual(lps_no_training_date.current_state, 'OUT')
        lps_fresh_last_report_and_no_training_date.update_current_state()
        self.assertEqual(
            lps_fresh_last_report_and_no_training_date.current_state, 'OUT')

    def _prepare_lps_and_pr(self, pr_creation_dates, lps_last_report_date,
                            avoid_state=None, lps_training_date=None):
        pr = mommy.make(core.models.ProgramReport, created=pr_creation_dates[0])
        for i in xrange(1, len(pr_creation_dates)):
            mommy.make(core.models.ProgramReport, created=pr_creation_dates[i],
                       site=pr.site, program=pr.program)
        lps = mommy.make(core.models.LocationProgramState, program=pr.program,
                         site=pr.site, last_report_date=lps_last_report_date,
                         training_date=lps_training_date)
        if avoid_state:
            self._set_current_state_to_different_than_given(lps, avoid_state)
        return lps

    def test_current_state_set_correctly_for_instances_with_program_reports(
            self):
        """Test instances of LocationProgramState for which at least one
        associated ProgramReport object exists in the system.
        The creation date of the newest ProgramReport object associated with a
        given instance of LocationProgramState should be used by
        update_current_state() when it tries to determine to which value the
        current_state attribute should be set.
        """
        weeks_ago = {}
        for wa in xrange(32, -1, -8):
            weeks_ago[wa] = self._current_state_date_with_delta(weeks_ago=wa)
        now = weeks_ago[0]
        date_list = weeks_ago.values()
        date_list.sort()
        # if there exist at least one program report
            # if newest report CREATE date newer than 8 weeks
        lps_no_last_report = self._prepare_lps_and_pr(
            pr_creation_dates=date_list, lps_last_report_date=None,
            avoid_state='ACTIVE')
        lps = self._prepare_lps_and_pr(
            pr_creation_dates=date_list, lps_last_report_date=now,
            avoid_state='ACTIVE')
                # ACTIVE
        lps_no_last_report.update_current_state()
        self.assertEqual(lps_no_last_report.current_state, 'ACTIVE')
        lps.update_current_state()
        self.assertEqual(lps.current_state, 'ACTIVE')
            # else if newest report CREATE date newer than 16 weeks
                # if last report date exists and newer than 8 weeks
        lps = self._prepare_lps_and_pr(pr_creation_dates=date_list[:-1],
                                       lps_last_report_date=now,
                                       avoid_state='ACTIVE-BAD')
                    # ACTIVE-BAD
        lps.update_current_state()
        self.assertEqual(lps.current_state, 'ACTIVE-BAD')
                # else (i.e. date does not exist or older than 8 weeks)
        lps_no_last_report = self._prepare_lps_and_pr(
            pr_creation_dates=date_list[:-1], lps_last_report_date=None,
            avoid_state='INACTIVE-NEW'
        )
        lps_over_8_weeks_old = self._prepare_lps_and_pr(
            pr_creation_dates=date_list[:-1],
            lps_last_report_date=weeks_ago[8],
            avoid_state='INACTIVE-NEW'
        )
                    # INACTIVE-NEW
        lps_no_last_report.update_current_state()
        self.assertEqual(lps_no_last_report.current_state, 'INACTIVE-NEW')
        lps_over_8_weeks_old.update_current_state()
        self.assertEqual(lps_over_8_weeks_old.current_state, 'INACTIVE-NEW')
            # else (i.e. newest report CREATE date older than 16 weeks)
                # if last report date exists and newer than 8 weeks
        lps = self._prepare_lps_and_pr(
            pr_creation_dates=date_list[:-2], lps_last_report_date=now,
            avoid_state='ACTIVE-BAD'
        )
                    # ACTIVE-BAD
        lps.update_current_state()
        self.assertEqual(lps.current_state, 'ACTIVE-BAD')
                # else (i.e. date does not exist or older than 8 weeks)
        lps_no_last_report = self._prepare_lps_and_pr(
            pr_creation_dates=date_list[:-2], lps_last_report_date=None,
            avoid_state='INACTIVE'
        )
        lps_over_8_weeks_old = self._prepare_lps_and_pr(
            pr_creation_dates=date_list[:-2],
            lps_last_report_date=weeks_ago[8],
            avoid_state='INACTIVE'
        )
                     # INACTIVE
        lps_no_last_report.update_current_state()
        self.assertEqual(lps_no_last_report.current_state, 'INACTIVE')
        lps_over_8_weeks_old.update_current_state()
        self.assertEqual(lps_over_8_weeks_old.current_state, 'INACTIVE')

    def _check_for_unwanted_side_effects_in_update_current_state(
            self, pr_dates, lps_last_report_date, lps_training_date=None):
        if pr_dates:
            lps = self._prepare_lps_and_pr(
                pr_creation_dates=pr_dates,
                lps_last_report_date=lps_last_report_date,
                lps_training_date=lps_training_date,
                avoid_state='OUT')
        else:
            lps = mommy.make(core.models.LocationProgramState,
                             last_report_date=lps_last_report_date,
                             training_date=lps_training_date)
        d0 = django.forms.models.model_to_dict(lps, exclude='current_state')
        lps.update_current_state()
        d1 = django.forms.models.model_to_dict(lps, exclude='current_state')
        self.assertEqual(
            set(d0.keys()), set(d1.keys()),
            'After running update_current_state() the list attributes of this '
            'LocationProgramState instance has changed.')
        for k in d0:
            value_before = str(d0[k])
            value_after = str(d1[k])
            self.assertEqual(
                value_before, value_after,
                'After running update_current_state() the value of attribute '
                '%s has changed from %s to %s.' % (k, value_before,
                                                   value_after))
        self.assertEqual(
            d0, d1, 'Unwanted side effects detected in a LocationProgramState '
                    'object after its update_current_state() method has been '
                    'run.')

    def test_update_current_state_has_no_unwanted_side_effects_on_instances(
            self):
        """Tests method update_current_state() for unwanted side effects.
        Instances of LocationProgramState should not be modified by the
        method under test apart from having the value of their current_state
        attribute set.
        """
        weeks_ago = {}
        for wa in xrange(32, -1, -8):
            weeks_ago[wa] = self._current_state_date_with_delta(weeks_ago=wa)
        now = weeks_ago[0]
        date_list = weeks_ago.values()
        date_list.sort()

        # if there are no program reports
            # if any training date exist
                # if last report date exists and newer than 8 weeks
                    # ACTIVE-BAD
        self._check_for_unwanted_side_effects_in_update_current_state(
            lps_training_date=now, lps_last_report_date=now, pr_dates=None)
                # else (i.e. date does not exist or older than 8 weeks)
                     # INACTIVE-TRAINED
        self._check_for_unwanted_side_effects_in_update_current_state(
            lps_training_date=now, lps_last_report_date=None, pr_dates=None)
        self._check_for_unwanted_side_effects_in_update_current_state(
            lps_training_date=now, lps_last_report_date=weeks_ago[8],
            pr_dates=None)
            # else (i.e. training date does not exist)
                # OUT
        self._check_for_unwanted_side_effects_in_update_current_state(
            lps_training_date=None, lps_last_report_date=None, pr_dates=None)
        self._check_for_unwanted_side_effects_in_update_current_state(
            lps_training_date=None, lps_last_report_date=now, pr_dates=None)

        # if there exist at least one program report
            # if newest report CREATE date newer than 8 weeks
                # ACTIVE
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list, lps_last_report_date=None)
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list, lps_last_report_date=now)
            # else if newest report CREATE date newer than 16 weeks
                # if last report date exists and newer than 8 weeks
                    # ACTIVE-BAD
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-1], lps_last_report_date=now)
                # else (i.e. date does not exist or older than 8 weeks)
                    # INACTIVE-NEW
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-1], lps_last_report_date=None)
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-1], lps_last_report_date=weeks_ago[8])
            # else (i.e. newest report CREATE date older than 16 weeks)
                # if last report date exists and newer than 8 weeks
                    # ACTIVE-BAD
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-2], lps_last_report_date=now)
                # else (i.e. date does not exist or older than 8 weeks)
                     # INACTIVE
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-2], lps_last_report_date=None)
        self._check_for_unwanted_side_effects_in_update_current_state(
            pr_dates=date_list[:-2], lps_last_report_date=weeks_ago[8])

    def _update_current_state_called_on_attribute_change(
            self, attribute_name, value):
        mommy.make(core.models.LocationProgramState)
        lps0 = core.models.LocationProgramState.objects.first()
        # Mock method LocationProgramState.update_current_state() before making
        # a change.
        with mock.patch.object(
                core.models.LocationProgramState, 'update_current_state',
                autospec=True
        ) as mock_ucs:
            # Employ a method equivalent to using the assignment operator.
            setattr(lps0, attribute_name, value)
        # Make sure that the mocked method has been called at least once (in
        # case of foreign keys and similar fields it is usually called twice -
        # once for the *_id and then once for the field itself).
        self.assertGreater(
            mock_ucs.call_count, 0, 'Method update_current_state() has not '
                                    'been called on %s change.' % attribute_name
        )

    def test_update_current_state_called_on_program_change(self):
        p0 = mommy.make(core.models.Program)
        self._update_current_state_called_on_attribute_change('program', p0)
        p1 = mommy.make(core.models.Program)
        self._update_current_state_called_on_attribute_change('program_id',
                                                              p1.id)

    def test_update_current_state_called_on_site_change(self):
        s0 = mommy.make(locations.models.Location)
        self._update_current_state_called_on_attribute_change('site', s0)
        s1 = mommy.make(locations.models.Location)
        self._update_current_state_called_on_attribute_change('site_id', s1.id)

    def test_update_current_state_called_on_last_report_date_change(self):
        self._update_current_state_called_on_attribute_change(
            'last_report_date', None)

    def test_update_current_state_called_on_training_date_change(self):
        self._update_current_state_called_on_attribute_change(
            'training_date', None)

    def test_correctly_saved(self):
        program = mommy.make(core.models.Program)
        site = mommy.make(locations.models.Location)
        lps = core.models.LocationProgramState(program=program, site=site)
        # There should be no LocationProgramState objects stored at this stage.
        number_of_saved_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_saved_objects, 0)
        # Serialise the original model object excluding id as it will change
        # from None to something else upon saving the object to the database.
        serialised0 = django.forms.models.model_to_dict(lps, exclude='id')
        lps.save()
        # There should be exactly one LocationProgramState object stored now.
        number_of_saved_objects = \
            core.models.LocationProgramState.objects.all().count()
        self.assertEqual(number_of_saved_objects, 1)
        # Is the object present in the system?
        self.assertIn(lps, core.models.LocationProgramState.objects.all())
        # To double-check, reacquire and serialise the saved model object
        # excluding id.  Compare with the serialised version of the original.
        saved_lps = core.models.LocationProgramState.objects.first()
        serialised1 = django.forms.models.model_to_dict(saved_lps, exclude='id')
        self.assertEqual(serialised0, serialised1,
                         'Saved object differs from the original.')

    def test_update_current_state_not_called_on_save(self):
        """Method update_current_state() used to be called on each save().  It
        has been decided that save() should not do this anymore.  This test is
        to prevent regressions.
        """
        program = mommy.make(core.models.Program)
        site = mommy.make(locations.models.Location)
        # Mock method LocationProgramState.update_current_state() before calling
        # method LocationProgramState.save().
        with mock.patch.object(
                core.models.LocationProgramState, 'update_current_state',
                autospec=True
        ) as mock_ucs:
            lps = core.models.LocationProgramState(program=program, site=site)
            lps.save()
        # Make sure that the mocked method has not been called.
        self.assertEqual(
            mock_ucs.call_count, 0, 'Method update_current_state() has been '
                                    'called by save() even though it should '
                                    'not.')

    def test_no_unique_key_constraint_on_site(self):
        # prepare required object
        l0 = mommy.make(locations.models.Location)
        mommy.make(core.models.LocationProgramState, site=l0)
        try:
            mommy.make(core.models.LocationProgramState, site=l0, _quantity=3)
        except django.db.IntegrityError as e:
            if 'duplicate key value violates unique constraint' in str(e):
                self.fail('Repeated association to the same site does not seem '
                          'to be allowed.  Original error message: %s' % e)
            else:
                raise e

    def test_unique_combination_of_program_and_site_enforced(self):
        # prepare required object
        l0, l1 = mommy.make(locations.models.Location, _quantity=2)
        p0, p1 = mommy.make(core.models.Program, _quantity=2)

        # objects with different combinations of program and site are allowed
        mommy.make(core.models.LocationProgramState, program=p0, site=l0)
        mommy.make(core.models.LocationProgramState, program=p0, site=l1)
        mommy.make(core.models.LocationProgramState, program=p1, site=l0)
        mommy.make(core.models.LocationProgramState, program=p1, site=l1)

        # no second object with the same combination of program and site allowed
        with self.assertRaisesRegexp(
                django.db.IntegrityError,
                'duplicate key value violates unique constraint'):
            mommy.make(core.models.LocationProgramState, program=p0, site=l0)
            mommy.make(core.models.LocationProgramState, program=p0, site=l1)
            mommy.make(core.models.LocationProgramState, program=p1, site=l0)
            mommy.make(core.models.LocationProgramState, program=p1, site=l1)
