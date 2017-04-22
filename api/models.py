from django.db import models
from torgomachi.settings import webhook_bot

# Create your models here.
class BotUser(models.Model):
    chat_id = models.PositiveIntegerField()
    username = models.CharField(max_length=100, blank=True, null=True)


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
        probability = .7
        return {
            'operation': Bot.BUY,
            'pair': Order.PAIR_EUR_USD,
            'probability': probability
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
        # fake success
        self.status = Order.STATUS_SUCCESS
        self.save()
        self.bot.balance += self.bid
        self.bot.save()

        webhook_bot.send_message(self.bot.user.chat_id, 'Сделка успешно завершена. Мы крутаны!!! XD')

