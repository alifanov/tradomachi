from django.core.management.base import BaseCommand, CommandError
from api.models import (Bot, BotUser, Signal)


class Command(BaseCommand):
    def handle(self, *args, **options):
        bu, _ = BotUser.objects.get_or_create(
            chat_id=1,
            username='BotUser#1'
        )
        bot, _ = Bot.objects.get_or_create(
            user=bu
        )
        signal, _ = Signal.objects.get_or_create(
            name='Median 30 minutes',
            slug='30min'
        )
        bot.signals.add(signal)
        signal, _ = Signal.objects.get_or_create(
            name='Median 90 minutes',
            slug='90min'
        )