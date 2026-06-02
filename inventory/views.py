from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Item, InventoryTransaction

class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/list.html'
    context_object_name = 'items'

class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'inventory/form.html'
    fields = ['name', 'description', 'category', 'unit', 'stock_quantity', 'low_stock_threshold', 'expiry_date', 'batch_number']
    success_url = reverse_lazy('inventory:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        InventoryTransaction.objects.create(
            item=self.object,
            transaction_type='ADD',
            quantity=self.object.stock_quantity,
            reason="Initial Stock",
            performed_by=self.request.user
        )
        return response

class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'inventory/detail.html'
    context_object_name = 'item'

class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'inventory/form.html'
    fields = ['name', 'description', 'category', 'unit', 'stock_quantity', 'low_stock_threshold', 'expiry_date', 'batch_number']
    success_url = reverse_lazy('inventory:list')

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'inventory/confirm_delete.html'
    success_url = reverse_lazy('inventory:list')

# Kit CRUD
from .models import Kit, KitItem

class KitListView(LoginRequiredMixin, ListView):
    model = Kit
    template_name = 'inventory/kit_list.html'
    context_object_name = 'kits'

class KitCreateView(LoginRequiredMixin, CreateView):
    model = Kit
    template_name = 'inventory/kit_form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('inventory:kit_list')

class KitDetailView(LoginRequiredMixin, DetailView):
    model = Kit
    template_name = 'inventory/kit_detail.html'
    context_object_name = 'kit'

class KitUpdateView(LoginRequiredMixin, UpdateView):
    model = Kit
    template_name = 'inventory/kit_form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('inventory:kit_list')

class KitDeleteView(LoginRequiredMixin, DeleteView):
    model = Kit
    template_name = 'inventory/kit_confirm_delete.html'
    success_url = reverse_lazy('inventory:kit_list')
