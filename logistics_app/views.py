from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from datetime import timedelta
from rest_framework import viewsets

from .models import Shipment, Order, Event, UserProfile
from .forms import ShipmentForm, OrderForm, EventForm, UserProfileForm, UserRegistrationForm
from .serializers import ShipmentSerializer, OrderSerializer, EventSerializer


# ====================================
# Custom Mixin for Role-Based Access
# ====================================
class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin to enforce role-based access control.
    Set `role_required` to specify required role.
    """
    role_required = None

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == self.role_required

    def handle_no_permission(self):
        return redirect('login')


# ====================================
# User Authentication & Profile Views
# ====================================

def register(request):
    """
    Handles user registration, sets passwords securely,
    and assigns roles via the UserProfile model.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            # Ensure UserProfile is created
            UserProfile.objects.get_or_create(user=new_user, defaults={'role': form.cleaned_data['role']})
            login(request, new_user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'logistics_app/register.html', {'form': form})


@login_required
def profile_view(request):
    """
    Renders and processes user profile updates.
    Supports AJAX responses for smoother UX.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            profile.refresh_from_db()  # Get latest data
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'role': profile.role})
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'logistics_app/profile.html', {'form': form})


# ====================================
# Home & Dashboard Views
# ====================================

def index(request):
    """
    Landing page with an introduction to Sports Logistics.
    """
    return render(request, 'logistics_app/index.html')


@login_required
def dashboard(request):
    """
    The main dashboard displaying statistics and analytics.
    """
    total_shipments = Shipment.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()

    today = timezone.now().date()
    shipments_by_date = [
        {'date': (today - timedelta(days=i)).strftime("%Y-%m-%d"),
         'count': Shipment.objects.filter(date_created__date=today - timedelta(days=i)).count()}
        for i in range(6, -1, -1)
    ]

    context = {
        'total_shipments': total_shipments,
        'pending_orders': pending_orders,
        'upcoming_events': upcoming_events,
        'shipments_by_date': shipments_by_date,
    }
    return render(request, 'logistics_app/dashboard.html', context)


# ====================================
# Shipment CRUD Views
# ====================================

class ShipmentListView(ListView):
    """
    Displays a list of shipments with a modal for creating new shipments.
    """
    model = Shipment
    template_name = 'logistics_app/shipments.html'
    context_object_name = 'shipments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ShipmentForm()  # Provides form for AJAX modal
        return context


class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'logistics_app/shipment_detail.html'
    context_object_name = 'shipment'


class ShipmentCreateView(RoleRequiredMixin, CreateView):
    """
    Allows warehouse managers to create shipments.
    """
    role_required = 'warehouse_manager'
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')


class ShipmentUpdateView(UpdateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')


class ShipmentDeleteView(DeleteView):
    model = Shipment
    template_name = 'logistics_app/shipment_confirm_delete.html'
    success_url = reverse_lazy('shipment_list')


# ====================================
# Order CRUD Views
# ====================================

class OrderListView(ListView):
    model = Order
    template_name = 'logistics_app/orders.html'
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'logistics_app/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'logistics_app/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')


# ====================================
# Event CRUD Views
# ====================================

class EventListView(ListView):
    model = Event
    template_name = 'logistics_app/events.html'
    context_object_name = 'events'


class EventDetailView(DetailView):
    model = Event
    template_name = 'logistics_app/event_detail.html'
    context_object_name = 'event'


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url = reverse_lazy('event_list')


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url = reverse_lazy('event_list')


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'logistics_app/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')


# ====================================
# API ViewSets (Django REST Framework)
# ====================================

class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
