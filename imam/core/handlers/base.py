from __future__ import unicode_literals

import re
from django.utils.translation import ugettext_lazy as _
from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler
from unidecode import unidecode


class BaseHandler(KeywordHandler):
    """Base keyword handler for application. Based on code from
    https://github.com/caktus/rapidsms-appointments
    """
    prefix = 'SAM'
    help_text = _('Please send {prefix} *COMMAND* to get help on *COMMAND*')
    form_class = None

    @classmethod
    def _keyword(cls):
        if hasattr(cls, 'keyword') and cls.keyword:
            pattern = r"^\s*(?:%s)\s*(?:%s)(?:[\s,;:]+(.+))?$" % (
                cls.prefix, cls.keyword
            )
        else:
            pattern = r"^\s*(?:%s)(\s*?)$" % cls.prefix
        return re.compile(pattern, re.IGNORECASE)

    def parse_message(self, text):
        raise NotImplementedError('This operation should only be used from a '
                                  'subclass of this class which should provide '
                                  'its own implementation.')

    def process_params(self, params):
        raise NotImplementedError('This operation should only be used from a '
                                  'subclass of this class which should provide '
                                  'its own implementation.')

    def handle(self, text):
        """Parse text, process commands and respond"""
        parsed = self.parse_message(text)

        if not self.form_class:
            return self.help()

        form = self.form_class(data=parsed, connection=self.msg.connections[0])

        if form.is_valid():
            params = form.save()

            response_message = self.process_params(params)

            self.respond(unidecode(response_message))
        else:
            error = form.error()

            if error is None:
                self.unknown()
            else:
                self.respond(unidecode(error))

        return True

    def help(self):
        if self.help_text:
            keyword = self.keyword or ''
            help_text = self.help_text.format(prefix=self.prefix.upper(),
                                              keyword=keyword.split('|')[
                                                  0].upper())
            self.respond(unidecode(help_text))

    def unknown(self):
        self.respond(unidecode(
            _('The SMS is not clear. Please review format and send again.')))
