from django.core.management.base import BaseCommand, CommandError
from api.models import Order, BotUser
from apns import APNs, Payload
from torgomachi.settings import PUSH_NOTIFICATIONS_SETTINGS


class Command(BaseCommand):
    def handle(self, *args, **options):
        for bu in BotUser.objects.filter(ios_id__isnull=False):
            offer = bu.bot.get_offer()
            if offer:
                apns = APNs(
                    use_sandbox=True,
                    cert_file=PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'],
                    key_file=PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'])
                payload = Payload(
                    alert="Зайди в аппу. Есть новый оффер.",
                    sound="default",
                    badge=1
                )
                apns.gateway_server.send_notification(bu.ios_id, payload)