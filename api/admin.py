from django.contrib import admin
from api.models import (Bot, Signal, BotUser, Order)

# Register your models here.
admin.site.register(Bot)
admin.site.register(Signal)
admin.site.register(BotUser)
admin.site.register(Order)
