from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Register API viewsets
router = DefaultRouter()
router.register(r'shipments', views.ShipmentViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    # Public Routes
    path('', views.index, name='index'),  # Landing Page (New Home)
    path('register/', views.register, name='register'),  # User Registration
    path('profile/', views.profile_view, name='profile'),  # User Profile

    # Authenticated Routes
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard Page

    # Shipments CRUD
    path('shipments/', views.ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/create/', views.ShipmentCreateView.as_view(), name='shipment_create'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    path('shipments/<int:pk>/update/', views.ShipmentUpdateView.as_view(), name='shipment_update'),
    path('shipments/<int:pk>/delete/', views.ShipmentDeleteView.as_view(), name='shipment_delete'),

    # Orders CRUD
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),

    # Events CRUD
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),

    # API Endpoints
    path('api/', include(router.urls)),  
]
