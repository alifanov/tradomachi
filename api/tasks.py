from api.models import Order
from django_rq import job

@job
def delayed_process_order(order_id):
    order = Order.objects.filter(id=order_id).first()
    if order:
        order.process()
