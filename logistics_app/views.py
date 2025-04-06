from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q  # For search filtering

from .models import Shipment, Order, Event, UserProfile
from .forms import ShipmentForm, OrderForm, EventForm, UserProfileForm, UserRegistrationForm
from .serializers import ShipmentSerializer, OrderSerializer, EventSerializer


# ====================================
# Custom Mixin for Role-Based Access
# ====================================
class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin to enforce role-based access control.
    Set `allowed_roles` as a list of roles that can access the view.
    """
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and hasattr(user, 'profile') and user.profile.role in self.allowed_roles

    def handle_no_permission(self):
        return redirect('dashboard')  # Redirect to dashboard instead of login


# ====================================
# User Authentication & Profile Views
# ====================================

def register(request):
    """ Handles user registration & assigns roles via UserProfile model. """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            UserProfile.objects.get_or_create(user=new_user, defaults={'role': form.cleaned_data['role']})
            login(request, new_user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'logistics_app/register.html', {'form': form})


@login_required
def profile_view(request):
    """ Renders & processes user profile updates. Supports AJAX updates. """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            profile.refresh_from_db()
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
    """ Landing page with an introduction to Sports Logistics. """
    return render(request, 'logistics_app/index.html')


@login_required
def dashboard(request):
    """ The main dashboard displaying statistics and analytics. """
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

class ShipmentListView(LoginRequiredMixin, ListView):
    """ Displays a list of shipments with AJAX support for tracking and search filtering. """
    model = Shipment
    template_name = 'logistics_app/shipments.html'
    context_object_name = 'shipments'

    def get_queryset(self):
        # Start with the base queryset
        queryset = super().get_queryset()
        # Get search query from URL (e.g., ?q=search_term)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(tracking_number__icontains=query) |
                Q(origin__icontains=query) |
                Q(destination__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the search query back to the template for display
        context['search_query'] = self.request.GET.get('q', '')
        context['form'] = ShipmentForm()
        return context


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    """ Displays detailed information about a shipment. """
    model = Shipment
    template_name = 'logistics_app/shipment_detail.html'
    context_object_name = 'shipment'


class ShipmentCreateView(RoleRequiredMixin, CreateView):
    """ Allows warehouse managers to create shipments. """
    allowed_roles = ['warehouse_manager']
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')


class ShipmentUpdateView(RoleRequiredMixin, UpdateView):
    """ Allows authorized users to update shipment details. """
    allowed_roles = ['warehouse_manager']
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')


class ShipmentDeleteView(RoleRequiredMixin, DeleteView):
    """ Allows warehouse managers to delete shipments. """
    allowed_roles = ['warehouse_manager']
    model = Shipment
    template_name = 'logistics_app/shipment_confirm_delete.html'
    success_url = reverse_lazy('shipment_list')


# ====================================
# Order CRUD Views
# ====================================

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'logistics_app/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(order_number__icontains=query) |
                Q(status__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        # Provide an instance of OrderForm if the user is an admin.
        if self.request.user.profile.role == 'admin':
            context['form'] = OrderForm()
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'logistics_app/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin']
    model = Order
    form_class = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model = Order
    form_class = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model = Order
    template_name = 'logistics_app/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')


# ====================================
# Event CRUD Views
# ====================================

class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'logistics_app/events.html'
    context_object_name = 'events'


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'logistics_app/event_detail.html'
    context_object_name = 'event'


class EventCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin']
    model = Event
    form_class = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url = reverse_lazy('event_list')


class EventUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model = Event
    form_class = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url = reverse_lazy('event_list')


class EventDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model = Event
    template_name = 'logistics_app/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')


# ====================================
# API ViewSets (Django REST Framework)
# ====================================

class ShipmentViewSet(viewsets.ModelViewSet):
    """ API Endpoint for managing shipments """
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
