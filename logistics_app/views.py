from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Shipment
from .forms import ShipmentForm

# Function-based view for the index page
def index(request):
    return render(request, 'logistics_app/index.html')

# List all shipments
class ShipmentListView(ListView):
    model = Shipment
    template_name = 'logistics_app/shipments.html'
    context_object_name = 'shipments'

# Detail view for a shipment (optional)
class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'logistics_app/shipment_detail.html'
    context_object_name = 'shipment'

# Create a new shipment
class ShipmentCreateView(CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')

# Update an existing shipment
class ShipmentUpdateView(UpdateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = 'logistics_app/shipment_form.html'
    success_url = reverse_lazy('shipment_list')

# Delete a shipment
class ShipmentDeleteView(DeleteView):
    model = Shipment
    template_name = 'logistics_app/shipment_confirm_delete.html'
    success_url = reverse_lazy('shipment_list')
