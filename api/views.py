from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from api.models import (Bot, Signal, BotUser, Order)
from api.serializers import *
# Create your views here.
from rest_framework.decorators import detail_route, list_route
from torgomachi.settings import webhook_bot, BASE_DIR, STICKER_START_FILE_ID

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
    print(message)
    if message.text == '/start':
        webhook_bot.send_sticker(message.chat.id, STICKER_START_FILE_ID)
        webhook_bot.send_message(message.chat.id, "Привет! Я енот Успех Успешных. Я умею торговать на валютном рынке и помогу тебе разбогатеть.")
    else:
        webhook_bot.reply_to(message, message.text)
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
