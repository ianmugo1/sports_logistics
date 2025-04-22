from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

# ——————————————————————————————————————————————————————
# Helper to auto-generate unique tracking numbers
# ——————————————————————————————————————————————————————
def generate_tracking_number() -> str:
    """
    Generate a unique, human-readable tracking code:
      SL + YYYYMMDD + 6 random hex chars
    Example: SL20250422A1B2C3
    """
    date_part = datetime.now().strftime('%Y%m%d')
    rand_part = uuid.uuid4().hex[:6].upper()
    return f"SL{date_part}{rand_part}"


class Event(models.Model):
    name        = models.CharField(max_length=100)
    date        = models.DateTimeField()
    location    = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name              = models.CharField(max_length=100)
    category          = models.CharField(max_length=100)
    quantity_in_stock = models.IntegerField(default=0)
    price             = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    description       = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('PENDING',    'Pending'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED',  'Delivered'),
    ]

    tracking_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_tracking_number,
        editable=False,
        help_text="Auto‑generated tracking code"
    )
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_created    = models.DateTimeField(auto_now_add=True)
    date_delivered  = models.DateTimeField(blank=True, null=True)
    origin          = models.CharField(max_length=200)
    destination     = models.CharField(max_length=200)
    contents        = models.TextField(blank=True, null=True)
    event           = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True)
    delivery_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='deliveries'
    )

    def __str__(self):
        return self.tracking_number


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('SHIPPED',   'Shipped'),
        ('DELIVERED', 'Delivered'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    order_date   = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    customer     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items        = models.ManyToManyField(Item, related_name='orders')
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.order_number


class Warehouse(models.Model):
    name      = models.CharField(max_length=100)
    location  = models.CharField(max_length=200)
    manager   = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='warehouses'
    )
    inventory = models.ManyToManyField(Item, related_name='warehouses')
    capacity  = models.IntegerField()

    def __str__(self):
        return self.name


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED',   'Completed'),
    ]

    shipment         = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='deliveries')
    assigned_person  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_deliveries'
    )
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    delivery_date    = models.DateTimeField(blank=True, null=True)
    delivery_location= models.CharField(max_length=200)

    def __str__(self):
        return f"Delivery for {self.shipment.tracking_number}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('CASH',        'Cash'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PENDING',   'Pending'),
        ('COMPLETED', 'Completed'),
    ]

    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status         = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_date   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('warehouse_manager', 'Warehouse Manager'),
        ('delivery_person',   'Delivery Person'),
        ('customer',          'Customer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.user.username} Profile"


# Signals to auto-create/save UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
