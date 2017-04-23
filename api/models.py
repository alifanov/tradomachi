import random
from django.db import models
from torgomachi.settings import *
from apns import APNs, Payload


def get_sticker(label, prefix='EMPTY'):
    return STICKERS[prefix][label]


def send_ios_notification(text, user, order_id):
    apns = APNs(
        use_sandbox=True,
        cert_file=PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'],
        key_file=PUSH_NOTIFICATIONS_SETTINGS['APNS_CERTIFICATE'])
    token_hex = user.ios_id
    payload = Payload(alert=text, sound="default", badge=1, custom={'order_id': order_id})
    apns.gateway_server.send_notification(token_hex, payload)


# Create your models here.
class BotUser(models.Model):
    chat_id = models.PositiveIntegerField(blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    ios_id = models.TextField(blank=True, null=True)
    with_etf = models.BooleanField(default=False)

    def get_sticker_prefix(self):
        return 'ETF' if self.bot.user.with_etf else 'EMPTY'

class Signal(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)


class Bot(models.Model):
    LEVEL_SCALE = 10.0

    BUY = 'buy'
    SELL = 'sell'
    NOOP = 'noop'

    START = 'start'

    user = models.OneToOneField(BotUser, related_name='bot')
    balance = models.PositiveIntegerField(default=100.0)

    signals = models.ManyToManyField(Signal, related_name='bots')

    def get_offer(self):
        prediction = self.predict()
        if prediction['probability'] > .51:
            return prediction
        return {}

    def order(self, operation, pair):
        if operation != Bot.NOOP:
            return Order.objects.create(
                bot=self,
                pair=pair,
                operation=operation
            )
        return None

    def toggle_signal(self, sid):
        if self.signals.filter(id=sid).exists():
            self.signals.remove(sid)
        else:
            self.signals.add(sid)

    def predict(self):
        if DEMO:
            return {
                'operation': random.choice([Bot.BUY, Bot.SELL]),
                'pair': random.choice([Order.PAIR_EUR_USD, Order.PAIR_USD_EUR]),
                'probability': random.uniform(0.3, 1.0)
            }
        else:
            return {
                'operation': random.choice([Bot.BUY, Bot.SELL]),
                'pair': random.choice([Order.PAIR_EUR_USD, Order.PAIR_USD_EUR]),
                'probability': random.uniform(.3, .4)
            }

    def get_level(self):
        return self.balance / Bot.LEVEL_SCALE


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    OPERATION_CHOICES = (
        (Bot.BUY, 'Buy'),
        (Bot.SELL, 'Sell')
    )

    PAIR_EUR_USD = 'EUR/USD'
    PAIR_USD_EUR = 'USD/EUR'

    PAIR_CHOICES = (
        (PAIR_EUR_USD, 'EUR/USD'),
        (PAIR_USD_EUR, 'USD/EUR'),
    )

    STATUS_FAIL = 'fail'
    STATUS_SUCCESS = 'success'
    STATUS_IN_PROGRESS = 'in_progress'

    STATUS_CHOICES = (
        (STATUS_FAIL, 'Fail'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_IN_PROGRESS, 'In progress'),
    )

    bid = models.PositiveIntegerField(default=10)
    pair = models.CharField(max_length=100, choices=PAIR_CHOICES)
    operation = models.CharField(max_length=100, choices=OPERATION_CHOICES)

    bot = models.ForeignKey(Bot, related_name='orders')

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_IN_PROGRESS)

    def process(self):
        is_success = random.choice([True, False])
        # fake success\fail
        if is_success:
            self.status = Order.STATUS_SUCCESS
            self.save()
            self.bot.balance += self.bid
            self.bot.save()

            if self.bot.user.chat_id:
                webhook_bot.send_sticker(self.bot.user.chat_id, get_sticker('STICKER_SUCCESS_FILE_ID', self.bot.user.get_sticker_prefix()))
                webhook_bot.send_message(self.bot.user.chat_id, 'Неплохо поднялись, босс!')
                webhook_bot.send_message(self.bot.user.chat_id, 'У тебя теперь ${}'.format(self.bot.balance))
            if self.bot.user.ios_id:
                send_ios_notification('Неплохо поднялись, босс!', self.bot.user, self.id)
        else:
            self.status = Order.STATUS_FAIL
            self.save()
            self.bot.balance -= self.bid
            self.bot.save()

            if self.bot.balance == 0:
                if self.bot.user.chat_id:
                    webhook_bot.send_sticker(self.bot.user.chat_id, get_sticker('STICKER_RIP_FILE_ID', self.bot.user.get_sticker_prefix()))
                    webhook_bot.send_message(self.bot.user.chat_id, 'Покойся с миром. Оживить за $100?')
                if self.bot.user.ios_id:
                    send_ios_notification('Покойся с миром. Оживить за $100?', self.bot.user, self.id)
            else:
                if self.bot.user.chat_id:
                    webhook_bot.send_sticker(self.bot.user.chat_id, get_sticker('STICKER_FAIL_FILE_ID', self.bot.user.get_sticker_prefix()))
                    webhook_bot.send_message(self.bot.user.chat_id, 'Что-то пошло не так')
                    webhook_bot.send_message(self.bot.user.chat_id, 'У тебя теперь ${}'.format(self.bot.balance))
                if self.bot.user.ios_id:
                    send_ios_notification('Что-то пошло не так', self.bot.user, self.id)

