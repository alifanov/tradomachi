from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from api.models import (Bot, Signal, BotUser, Order, get_sticker)
from api.tasks import delayed_process_order
from api.serializers import *
# Create your views here.
from rest_framework.decorators import detail_route, list_route
from torgomachi.settings import *

import os
import telebot
import ujson


class BotViewset(ModelViewSet):
    serializer_class = BotSeralizer

    @list_route(methods=['post'])
    def toggle_signals(self, request):
        bot = self.get_queryset().first()
        sids = request.data['signals']
        for sid in sids:
            bot.toggle_signal(sid)
        return Response(BotSeralizer(bot).data)

    @list_route(methods=['post'])
    def order(self, request):
        bot = self.get_queryset().first()
        operation = request.data['operation']
        pair = request.data['pair']

        order = bot.order(
            operation=operation,
            pair=pair
        )

        delayed_process_order.delay(order.id)
        return Response(BotSeralizer(bot).data)

    @list_route(methods=['post'])
    def register(self, request):

        bot_user, _ = BotUser.objects.get_or_create(ios_id=request.data['ios_id'])
        bot, _ = Bot.objects.get_or_create(user=bot_user)

        return Response(BotSeralizer(bot).data)

    def get_queryset(self):
        if 'ios_id' not in self.request.query_params:
            return HttpResponseForbidden()
        self.bot_user = BotUser.objects.get(ios_id=self.request.query_params['ios_id'])
        return Bot.objects.filter(user=self.bot_user)


class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        update = telebot.types.Update.de_json(ujson.dumps(request.data))
        webhook_bot.process_new_updates([update])
        return HttpResponse('')


@webhook_bot.message_handler(func=lambda message: True, content_types=['text', 'sticker'])
def echo_message(message):
    # print(message)

    bot_user, _ = BotUser.objects.get_or_create(chat_id=message.chat.id)
    Bot.objects.get_or_create(user=bot_user)

    if message.text == '/start':
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Есть чо?')
        webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_BORN_FILE_ID', bot_user.get_sticker_prefix()))
        webhook_bot.send_message(
            message.chat.id,
            "Привет! Я охреннный енотик, я точно знаю как делать деньги. Готов?",
            reply_markup=markup
        )
        webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_WELCOME_FILE_ID', bot_user.get_sticker_prefix()))
    elif message.text in ['Нет', 'Не хочу']:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Есть чо?')
        webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_SKIP_FILE_ID', bot_user.get_sticker_prefix()))
        webhook_bot.send_message(
            message.chat.id,
            "OK, буду искать другие сделки :)",
            reply_markup=markup
        )
    elif message.text == 'Да':
        offer = bot_user.bot.get_offer()
        order = bot_user.bot.order(offer['operation'], offer['pair'])

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Есть чо?')

        webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_WAIT_FILE_ID', bot_user.get_sticker_prefix()))
        webhook_bot.send_message(
            message.chat.id,
            "Подожди... сейчас будет",
            reply_markup=markup
        )

        delayed_process_order.delay(order.id)

    elif message.text == 'Беру':
        bot_user.with_etf = True
        bot_user.save()

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Есть чо?')

        webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_ETF_BOUGHT_FILE_ID', bot_user.get_sticker_prefix()))
        webhook_bot.send_message(
            message.chat.id,
            "Закупился. Теперь ждем подъема :)",
            reply_markup=markup
        )

    elif message.text == 'Есть чо?':
        if random.uniform(0.4, 1.0) < 0.5:

            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Беру', 'Не хочу')

            webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_OFFER_FILE_ID', bot_user.get_sticker_prefix()))
            webhook_bot.send_message(
                message.chat.id,
                "ETF: Говорят надо брать SPDR. Сейчас самая низкая цена за последние 90 дней.".format(),
                reply_markup=markup
            )
        else:

            offer = bot_user.bot.get_offer()

            if offer:

                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('Да', 'Нет')

                webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_OFFER_FILE_ID', bot_user.get_sticker_prefix()))
                webhook_bot.send_message(
                    message.chat.id,
                    "{0} {1}?! (инфа {2:.2%})".format(
                        {
                            'buy': 'Покупаем',
                            'sell': 'Продаем'
                        }[offer['operation']],
                        offer['pair'].upper(),
                        offer['probability']
                    ),
                    reply_markup=markup
                )
            else:
                webhook_bot.send_sticker(message.chat.id, get_sticker('STICKER_NO_DEAL_FILE_ID', bot_user.get_sticker_prefix()))
                markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('Есть чо?')
                webhook_bot.send_message(
                    message.chat.id,
                    "Увы, но пока нет подходящих сделок на рынке",
                    reply_markup=markup
                )
    else:
        webhook_bot.reply_to(message, "OK")
