from django.core.management.base import BaseCommand, CommandError
from api.models import Order
from api.tasks import delayed_process_order


class Command(BaseCommand):
    def handle(self, *args, **options):
        for order in Order.objects.filter(status=Order.STATUS_IN_PROGRESS):
            delayed_process_order.delay(order.id)
