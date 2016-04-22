from __future__ import unicode_literals

import re
from django.utils.translation import ugettext_lazy as _
from rapidsms.models import Contact

from .base import BaseHandler
from ..forms import RegistrationForm
from ..models import Personnel


email_pattern = re.compile('.*@.*')


class RegistrationHandler(BaseHandler):
    form_class = RegistrationForm
    help_text = _(
        'Send {prefix} {keyword} SITE-ID Name Lastname Position Email '
        '(optional) to register'
    )
    keyword = 'reg'
    success_text = _(
        'Thank you {name}, {position}, you are registered at {site_name} '
        'with the site ID {site_id} in {loc}'
    )

    def parse_message(self, text):
        parsed = {'site_id': None, 'name': None, 'position_code': None,
                  'email': None}
        words = text.split()

        parsed['site_id'] = words.pop(0)

        try:
            if email_pattern.match(words[-1]):
                parsed['email'] = words.pop()

            parsed['position_code'] = words.pop()
        except IndexError:
            pass

        parsed['name'] = ' '.join((word.capitalize() for word in words))

        return parsed

    def process_params(self, params):
        contact = params['connection'].contact
        parent_loc_name = params['site'].parent.name if params[
            'site'].parent else ''

        if contact:
            worker = contact.worker

            if (worker.name == params['name']) and (
                worker.site == params['site']) and (
                worker.email == params['email']) and (
                worker.position == params['position']
            ):
                response = _('{name} has already registered').format(
                    name=params['name'])
                return response
            else:
                worker.name = params['name']
                worker.email = params['email']
                worker.site = params['site']
                worker.position = params['position']

                worker.save()
                response = self.success_text.format(name=params['name'],
                                                    position=params['position'],
                                                    site_name=params[
                                                        'site'].name,
                                                    site_id=params['site'].hcid,
                                                    loc=parent_loc_name)
                return response

        contact = Contact.objects.create(name=params['name'])
        params['connection'].contact = contact
        params['connection'].save()

        Personnel.objects.create(contact=contact, email=params['email'],
                                 name=params['name'], site=params['site'],
                                 position=params['position'])
        response = self.success_text.format(name=params['name'],
                                            position=params['position'],
                                            site_name=params['site'].name,
                                            site_id=params['site'].hcid,
                                            loc=parent_loc_name)

        return response
