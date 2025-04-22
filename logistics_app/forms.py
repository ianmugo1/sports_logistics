from django import forms
from django.contrib.auth.models import User
from django_select2.forms import Select2TagWidget
from .models import Shipment, Order, Event, UserProfile, Warehouse
import uuid

# -----------------------------------
# Shipment Form (tracking hidden)
# -----------------------------------
class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        # omit tracking_number & date_created—they're auto‑generated
        fields = [
            'status',
            'date_delivered',
            'origin',
            'destination',
            'contents',
            'event',
            'delivery_person',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'date_delivered': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'origin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Origin'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination'}),
            'contents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'delivery_person': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ensure datetime widget matches instance formatting
        if self.instance and self.instance.date_delivered:
            self.initial['date_delivered'] = self.instance.date_delivered.strftime('%Y-%m-%dT%H:%M')


# -----------------------------------
# Order Form (excludes order_date)
# -----------------------------------
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # omit order_date (auto_now_add)
        fields = [
            'order_number',
            'status',
            'customer',
            'items',
            'total_price',
        ]
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to auto‑generate'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'items': Select2TagWidget(attrs={'class': 'form-control'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('order_number'):
            # 10‑char uppercase UUID segment
            cleaned['order_number'] = uuid.uuid4().hex[:10].upper()
        return cleaned


# -----------------------------------
# Event Form
# -----------------------------------
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'date':        forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'location':    forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.date:
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%dT%H:%M')


# -----------------------------------
# Warehouse Form
# -----------------------------------
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'capacity']
        widgets = {
            'name':     forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# -----------------------------------
# User Profile & Registration Forms
# -----------------------------------
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirm Password'
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email':    forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError("Passwords don't match.")
        return cd.get('password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # create or update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        return user
