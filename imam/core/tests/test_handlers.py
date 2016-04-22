from __future__ import unicode_literals


__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'


import mock


from rapidsms.tests.harness import RapidTest


from ..handlers.base import BaseHandler
from ..handlers.registration import RegistrationHandler
from ..handlers.stockout import StockoutReportHandler


class BaseHandlerTest(RapidTest):
    def test_help_message(self):
        responses = BaseHandler.test(BaseHandler.prefix)
        control_response = 'Please send {prefix} *COMMAND* to get help on ' \
                           '*COMMAND*'.format(prefix=BaseHandler.prefix.upper())

        self.assertTrue(responses)
        self.assertEqual(responses[0], control_response)


class RegistrationHandlerTest(RapidTest):
    def test_help_message(self):
        responses = RegistrationHandler.test(
            '{prefix} {keyword}'.format(prefix=RegistrationHandler.prefix,
                                        keyword=RegistrationHandler.keyword))
        control_response = 'Send SAM REG SITE-ID Name Lastname Position ' \
                           'Email (optional) to register'
        self.assertTrue(responses)
        self.assertEqual(responses[0], control_response)


class StockoutHandlerTest(RapidTest):
    def test_handle_does_not_fail_when_empty_text_message_received(self):
        message = mock.MagicMock()
        router = mock.MagicMock()
        handler = StockoutReportHandler(router, message)
        handler.handle(text='')

    def test_item_codes_from_parse_message_called_with_empty_text_is_a_set(
            self
    ):
        message = mock.MagicMock()
        router = mock.MagicMock()
        handler = StockoutReportHandler(router, message)
        parsed = handler.parse_message(text='')
        item_codes = parsed['item_codes']
        self.assertIsInstance(item_codes, set)

    def test_help_message(self):
        text = '{prefix} {keyword}'.format(
            prefix=StockoutReportHandler.prefix,
            keyword=StockoutReportHandler.keyword.split('|')[0]
        )
        control_response = 'To report a stock out, send OUT StockCode'

        responses = StockoutReportHandler.test(text=text)
        self.assertTrue(responses)
        self.assertEqual(responses[0], control_response)
