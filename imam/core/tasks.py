from celery import task
from .models import LowStockAlert, StockOutReport


@task
def reminders():
    for alert in LowStockAlert.objects.all():
        alert.generate_notification()

    for stockout in StockOutReport.objects.all():
        stockout.generate_notification()
