from rest_framework import serializers
from api.models import *


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

    def get_signals(self, obj):
        return [dict(SignalSeralizer(s).data, **{'enabled': obj.signals.filter(id=s.id).exists()}) for s in Signal.objects.all()]

    class Meta:
        model = Bot
        fields = (
            'id',
            'balance',
            'signals'
        )

