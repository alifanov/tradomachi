from rest_framework import serializers
from api.models import *


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'id',
            'created_at',
            'bid',
            'pair',
            'operation',
            'status'
        )


class SignalSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = (
            'id',
            'name',
            'slug',
        )


class BotSeralizer(serializers.ModelSerializer):
    signals = serializers.SerializerMethodField()
    offer = serializers.DictField(source='get_offer')
    orders = OrderSerializer(read_only=True, many=True)
    level = serializers.SerializerMethodField()

    def get_level(self, obj):
        return obj.get_level()

    def get_signals(self, obj):
        return [dict(SignalSeralizer(s).data, **{'enabled': obj.signals.filter(id=s.id).exists()}) for s in
                Signal.objects.all()]

    class Meta:
        model = Bot
        fields = (
            'id',
            'balance',
            'signals',
            'offer',
            'orders',
            'level'
        )
