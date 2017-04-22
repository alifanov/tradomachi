from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from api.models import (Bot, Signal, BotUser, Order)
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
        bot.order(
            operation=operation,
            pair=pair
        )
        return Response(BotSeralizer(bot).data)

    def get_queryset(self):
        if 'chat_id' not in self.request.query_params:
            return HttpResponseForbidden()
        self.bot_user = BotUser.objects.get(chat_id=self.request.query_params['chat_id'])
        return Bot.objects.filter(user=self.bot_user)


class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        update = telebot.types.Update.de_json(ujson.dumps(request.data))
        webhook_bot.process_new_updates([update])
        return HttpResponse('')


# @webhook_bot.message_handler(func=lambda message: True, commands=['start'])
# def start_handler(message):
    # webhook_bot.send_sticker(message.chat.id, STICKER_START_FILE_ID)
    # webhook_bot.send_message(message.chat.id, "Привет! Я енот Успех Успешных. Я умею торговать на валютном рынке и помогу тебе разбогатеть.")


@webhook_bot.message_handler(func=lambda message: True, content_types=['text', 'sticker'])
def echo_message(message):
    # print(message)

    bot_user, _ = BotUser.objects.get_or_create(chat_id=message.chat.id)
    Bot.objects.get_or_create(user=bot_user)

    if message.text == '/start':
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('/offer')
        webhook_bot.send_sticker(message.chat.id, STICKER_BORN_FILE_ID)
        webhook_bot.send_message(
            message.chat.id,
            "Привет! Я енот Успех Успешных. Я умею торговать на валютном рынке и помогу тебе разбогатеть.",
            reply_markup=markup
        )
        webhook_bot.send_sticker(message.chat.id, STICKER_WELCOME_FILE_ID)
    elif message.text == '/clear':
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('/offer')
        webhook_bot.send_sticker(message.chat.id, STICKER_SKIP_FILE_ID)
        webhook_bot.send_message(
            message.chat.id,
            "OK, буду искать другие сделки :)",
            reply_markup=markup
        )
    elif message.text == '/order':
        offer = bot_user.bot.get_offer()
        order = bot_user.bot.order(offer['operation'], offer['pair'])

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('/offer')

        webhook_bot.send_message(
            message.chat.id,
            "Ордер создан. Скоро узнаем на сколько мы везучие ))",
            reply_markup=markup
        )

        delayed_process_order.delay(order.id)

    elif message.text == '/offer':
        offer = bot_user.bot.get_offer()

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('/order')
        markup.add('/clear')

        webhook_bot.send_message(
            message.chat.id,
            "Есть интересная сделка. {} для пары {}. Вероятность успеха: {}%".format(
                offer['operation'].capitalize(),
                offer['pair'].upper(),
                offer['probability']*100
            ),
            reply_markup=markup
        )
    else:
        webhook_bot.reply_to(message, "OK")
    # webhook_bot.send_sticker(message.chat.id, open(os.path.join(BASE_DIR, 'images', 'start.png'), 'rb').read())
    # webhook_bot.send_message(message.chat.id, message.text)


class StartView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        response_data = {}

        # get user
        user, created = BotUser.objects.get_or_create(
            chat_id=data['message']['chat']['id']
        )
        if created:
            user.username = data['message']['username']
            user.save()

        operation = data.get('operation')
        # agree order
        if operation:
            user.bot.order(
                operation=operation,
                pait=data['pair']
            )

        return Response(response_data)
