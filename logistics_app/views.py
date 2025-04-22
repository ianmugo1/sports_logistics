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
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, DurationField
from django.contrib import messages

from .models import Shipment, Order, Event, UserProfile, Warehouse
from .forms import (
    ShipmentForm, OrderForm, EventForm,
    UserProfileForm, UserRegistrationForm, WarehouseForm
)
from .serializers import ShipmentSerializer, OrderSerializer, EventSerializer


# ====================================
# Custom Mixin for Role‑Based Access
# ====================================
class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        return (
            user.is_authenticated and
            hasattr(user, 'profile') and
            user.profile.role in self.allowed_roles
        )

    def handle_no_permission(self):
        return redirect('dashboard')


# ====================================
# Authentication & Profile Views
# ====================================
def register(request):
    """User registration with role assignment."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            UserProfile.objects.get_or_create(
                user=new_user,
                defaults={'role': form.cleaned_data['role']}
            )
            login(request, new_user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'logistics_app/register.html', {'form': form})


@login_required
def profile_view(request):
    """View & update user profile (AJAX supported)."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'role': profile.role})
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    return render(request, 'logistics_app/profile.html', {'form': form})


# ====================================
# Landing & Dashboard
# ====================================
def index(request):
    """Landing page."""
    return render(request, 'logistics_app/index.html')


@login_required
def dashboard(request):
    """
    Single dashboard view:
      - summary stats
      - 7‑day shipments chart (date_labels, shipment_counts)
      - recent shipments list
    """
    today = timezone.now().date()

    # Shipments per day (last 7 days)
    shipments_by_date = [
        {
            'date': (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            'count': Shipment.objects.filter(
                date_created__date=today - timedelta(days=i)
            ).count()
        }
        for i in range(6, -1, -1)
    ]

    # Extract two simple lists for Chart.js
    date_labels     = [d['date']  for d in shipments_by_date]
    shipment_counts = [d['count'] for d in shipments_by_date]

    # 5 most recent shipments
    recent_shipments = Shipment.objects.filter(
        date_created__date__gte=today - timedelta(days=7)
    ).order_by('-date_created')[:5]

    context = {
        'total_shipments':   Shipment.objects.count(),
        'pending_orders':    Order.objects.filter(status='PENDING').count(),
        'upcoming_events':   Event.objects.filter(date__gte=timezone.now()).count(),
        'date_labels':       date_labels,
        'shipment_counts':   shipment_counts,
        'recent_shipments':  recent_shipments,
    }
    return render(request, 'logistics_app/dashboard.html', context)


# ====================================
# Analytics Endpoints & View
# ====================================
@login_required
def analytics_data(request):
    """
    Returns JSON:
      - shipments_by_date (last 7 days)
      - orders_by_status
      - avg delivery time (last 30 days, in seconds)
    """
    today = timezone.now().date()
    shipments_by_date = [
        {
            'date': (today - timedelta(days=i)).strftime("%Y-%m-%d"),
            'count': Shipment.objects.filter(
                date_created__date=today - timedelta(days=i)
            ).count()
        }
        for i in range(6, -1, -1)
    ]
    orders_by_status = list(
        Order.objects
             .values('status')
             .annotate(count=Count('id'))
             .order_by('status')
    )
    thirty_days_ago = timezone.now() - timedelta(days=30)
    avg_delta = Shipment.objects.filter(
        date_delivered__gte=thirty_days_ago
    ).annotate(
        delivery_time=ExpressionWrapper(
            F('date_delivered') - F('date_created'),
            output_field=DurationField()
        )
    ).aggregate(avg=Avg('delivery_time'))['avg']
    avg_seconds = avg_delta.total_seconds() if avg_delta else None

    return JsonResponse({
        'shipments_by_date':    shipments_by_date,
        'orders_by_status':     orders_by_status,
        'avg_delivery_seconds': avg_seconds,
    })


@login_required
def analytics_view(request):
    """Renders the analytics dashboard shell."""
    return render(request, 'logistics_app/analytics.html')


# ====================================
# Shipment Tracking View
# ====================================
def track_shipment(request):
    """
    Search by full or partial tracking number:
      - if exactly 1 match → detail view
      - otherwise → list view
    """
    term = (request.GET.get('tracking_number') or "").strip()
    if term:
        shipments = Shipment.objects.filter(tracking_number__icontains=term)
    else:
        shipments = Shipment.objects.none()

    if term and shipments.count() == 1:
        return render(request, 'logistics_app/track_shipment_detail.html', {
            'shipment': shipments.first()
        })

    return render(request, 'logistics_app/track_shipment_list.html', {
        'shipments':   shipments,
        'search_term': term,
    })


# ====================================
# Shipment CRUD
# ====================================
class ShipmentListView(LoginRequiredMixin, ListView):
    model = Shipment
    template_name = 'logistics_app/shipments.html'
    context_object_name = 'shipments'

    def get_queryset(self):
        qs = super().get_queryset()
        q  = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(tracking_number__icontains=q) |
                Q(origin__icontains=q) |
                Q(destination__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['form']         = ShipmentForm()
        return ctx


class ShipmentDetailView(LoginRequiredMixin, DetailView):
    model = Shipment
    template_name = 'logistics_app/shipment_detail.html'
    context_object_name = 'shipment'


class ShipmentCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['warehouse_manager']
    model         = Shipment
    form_class    = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url   = reverse_lazy('shipment_list')


class ShipmentUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['warehouse_manager']
    model         = Shipment
    form_class    = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url   = reverse_lazy('shipment_list')


class ShipmentDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['warehouse_manager']
    model         = Shipment
    template_name = 'logistics_app/shipment_confirm_delete.html'
    success_url   = reverse_lazy('shipment_list')


# ====================================
# Order CRUD
# ====================================
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'logistics_app/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        qs = super().get_queryset()
        q  = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(order_number__icontains=q) |
                Q(status__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        if self.request.user.profile.role == 'admin':
            ctx['form'] = OrderForm()
        return ctx


class OrderDetailView(LoginRequiredMixin, DetailView):
    model             = Order
    template_name     = 'logistics_app/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin']
    model         = Order
    form_class    = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url   = reverse_lazy('order_list')

    def form_valid(self, form):
        messages.success(self.request, "Order created successfully!")
        return super().form_valid(form)


class OrderUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model         = Order
    form_class    = OrderForm
    template_name = 'logistics_app/order_form.html'
    success_url   = reverse_lazy('order_list')


class OrderDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model         = Order
    template_name = 'logistics_app/order_confirm_delete.html'
    success_url   = reverse_lazy('order_list')


# ====================================
# Event CRUD
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
    model         = Event
    form_class    = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url   = reverse_lazy('event_list')


class EventUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin']
    model         = Event
    form_class    = EventForm
    template_name = 'logistics_app/event_form.html'
    success_url   = reverse_lazy('event_list')


class EventDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model         = Event
    template_name = 'logistics_app/event_confirm_delete.html'
    success_url   = reverse_lazy('event_list')


# ====================================
# Warehouse CRUD
# ====================================
class WarehouseListView(RoleRequiredMixin, ListView):
    allowed_roles      = ['admin', 'warehouse_manager']
    model              = Warehouse
    template_name      = 'logistics_app/warehouses.html'
    context_object_name = 'warehouses'


class WarehouseCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ['admin', 'warehouse_manager']
    model         = Warehouse
    form_class    = WarehouseForm
    template_name = 'logistics_app/warehouse_form.html'
    success_url   = reverse_lazy('warehouse_list')


class WarehouseUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ['admin', 'warehouse_manager']
    model         = Warehouse
    form_class    = WarehouseForm
    template_name = 'logistics_app/warehouse_form.html'
    success_url   = reverse_lazy('warehouse_list')


class WarehouseDeleteView(RoleRequiredMixin, DeleteView):
    allowed_roles = ['admin']
    model         = Warehouse
    template_name = 'logistics_app/warehouse_confirm_delete.html'
    success_url   = reverse_lazy('warehouse_list')


# ====================================
# API ViewSets
# ====================================
class ShipmentViewSet(viewsets.ModelViewSet):
    queryset         = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    queryset         = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    queryset         = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
