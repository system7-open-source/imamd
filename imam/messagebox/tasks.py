from celery import task
from celery.utils.log import get_task_logger
from rapidsms.router.api import lookup_connections, send
from django.conf import settings

logger = get_task_logger(__name__)


def _send_sms(message, *recipients):
    backend = settings.BULKSMS_BACKEND
    connections = lookup_connections(backend, recipients)

    send(message, connections)


@task()
def send_sms(message, *recipients):
    if len(recipients) == 0:
        logger.warn('send_sms task called with empty recipient list')
        return

    _send_sms(message, *recipients)
