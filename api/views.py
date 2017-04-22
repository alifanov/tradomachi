from django.shortcuts import render
from django.http import HttpResponseForbidden
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from api.models import (Bot, Signal, BotUser, Order)
from api.serializers import *
# Create your views here.
from rest_framework.decorators import detail_route, list_route


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