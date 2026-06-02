from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Distribution, DistributionItem
from beneficiaries.models import Beneficiary
from inventory.models import Item
from events.models import ReliefEvent

class DistributionListView(LoginRequiredMixin, ListView):
    model = Distribution
    template_name = 'distribution/list.html'
    context_object_name = 'distributions'

class DistributionCreateView(LoginRequiredMixin, CreateView):
    model = Distribution
    template_name = 'distribution/form.html'
    fields = ['event', 'beneficiary', 'proof_photo', 'notes']
    success_url = reverse_lazy('distribution:list')

    def form_valid(self, form):
        form.instance.distributed_by = self.request.user
        form.instance.verification_status = True
        
        # Mark beneficiary as claimed
        beneficiary = form.cleaned_data.get('beneficiary')
        beneficiary.claim_status = 'CLAIMED'
        beneficiary.save()
        
        return super().form_valid(form)

class DistributionDetailView(LoginRequiredMixin, DetailView):
    model = Distribution
    template_name = 'distribution/detail.html'
    context_object_name = 'distribution'

class DistributionUpdateView(LoginRequiredMixin, UpdateView):
    model = Distribution
    template_name = 'distribution/form.html'
    fields = ['event', 'beneficiary', 'proof_photo', 'notes']
    success_url = reverse_lazy('distribution:list')

class DistributionDeleteView(LoginRequiredMixin, DeleteView):
    model = Distribution
    template_name = 'distribution/confirm_delete.html'
    success_url = reverse_lazy('distribution:list')

def verify_qr(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data', '').strip()
        
        if not qr_data:
            messages.warning(request, "Please enter a reference number or scan a QR code.")
            return render(request, 'distribution/verify_qr.html')

        ref = None
        # Handle full QR format: REF:XXXX|NAME:XXXX
        if qr_data.startswith('REF:'):
            ref = qr_data.split('|')[0].replace('REF:', '').strip()
        else:
            # Handle raw reference number
            ref = qr_data

        beneficiary = Beneficiary.objects.filter(claim_reference_number=ref).first()
        
        if beneficiary:
            messages.success(request, f"Beneficiary verified: {beneficiary.full_name}")
            return redirect('beneficiaries:detail', pk=beneficiary.pk)
        else:
            messages.error(request, f"No beneficiary found with reference: {ref}")
            
    return render(request, 'distribution/verify_qr.html')
