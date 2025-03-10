from django import forms
from .models import Shipment

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_number', 'status', 'origin', 'destination', 'contents', 'event', 'delivery_person']
