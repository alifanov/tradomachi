from django.core.management.base import BaseCommand, CommandError
from apns import APNs, Payload
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        apns = APNs(
            use_sandbox=True,
            cert_file=settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'],
            key_file=settings.PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'])
        token_hex = '104636f177046985d0a728735f2b583d26885bd9f4a29f833c0922bf5a1ec906'
        payload = Payload(alert="Ура!!! Новая сделака - вероятность 70%.", sound="default", badge=1)
        apns.gateway_server.send_notification(token_hex, payload)