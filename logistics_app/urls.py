from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Register API ViewSets
router = DefaultRouter()
router.register(r'shipments', views.ShipmentViewSet)
router.register(r'orders',    views.OrderViewSet)
router.register(r'events',    views.EventViewSet)

urlpatterns = [
    # ============================================
    # Public Routes (Accessible to Everyone)
    # ============================================
    path('',            views.index,          name='index'),      # Landing Page
    path('register/',   views.register,       name='register'),   # User Registration

    # ============================================
    # Authentication Routes (Login, Logout, etc.)
    # ============================================
    path('accounts/', include('django.contrib.auth.urls')),
    # Includes: /accounts/login/, /accounts/logout/, /accounts/password_change/, /accounts/password_reset/, etc.

    # ============================================
    # Analytics (Requires Login)
    # ============================================
    path('analytics/data/', views.analytics_data, name='analytics_data'),
    path('analytics/',      views.analytics_view, name='analytics'),

    # ============================================
    # Authenticated Routes (Requires Login)
    # ============================================
    path('dashboard/', views.dashboard,     name='dashboard'),
    path('profile/',   views.profile_view, name='profile'),

    # ============================================
    # Shipment Tracking (Public or Authenticated)
    # ============================================
    path('track/', views.track_shipment, name='track_shipment'),

    # ============================================
    # Shipment Management (Warehouse Managers)
    # ============================================
    path('shipments/',          views.ShipmentListView.as_view(),   name='shipment_list'),
    path('shipments/create/',   views.ShipmentCreateView.as_view(), name='shipment_create'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    path('shipments/<int:pk>/update/', views.ShipmentUpdateView.as_view(), name='shipment_update'),
    path('shipments/<int:pk>/delete/', views.ShipmentDeleteView.as_view(), name='shipment_delete'),

    # ============================================
    # Order Management (Admins)
    # ============================================
    path('orders/',          views.OrderListView.as_view(),   name='order_list'),
    path('orders/create/',   views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),

    # ============================================
    # Event Management (Admins)
    # ============================================
    path('events/',          views.EventListView.as_view(),   name='event_list'),
    path('events/create/',   views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # ============================================
    # Warehouse Management (Admin & Managers)
    # ============================================
    path('warehouses/',        views.WarehouseListView.as_view(),   name='warehouse_list'),
    path('warehouses/create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses/<int:pk>/update/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouses/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse_delete'),

    # ============================================
    # API Endpoints (Django REST Framework)
    # ============================================
    path('api/', include(router.urls)),
]
