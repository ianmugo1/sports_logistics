from django.contrib import admin
from .models import Event, Item, Shipment, Order, Warehouse, Delivery, Payment

admin.site.register(Event)
admin.site.register(Item)
admin.site.register(Shipment)
admin.site.register(Order)
admin.site.register(Warehouse)
admin.site.register(Delivery)
admin.site.register(Payment)
