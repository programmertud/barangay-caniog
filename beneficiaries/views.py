from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Beneficiary, Category, FamilyMember
from .forms import FamilyMemberForm

class FamilyMemberCreateView(LoginRequiredMixin, CreateView):
    model = FamilyMember
    form_class = FamilyMemberForm
    template_name = 'beneficiaries/family_member_form.html'

    def form_valid(self, form):
        beneficiary = get_object_or_404(Beneficiary, pk=self.kwargs['pk'])
        form.instance.beneficiary = beneficiary
        messages.success(self.request, f"Family member added to {beneficiary.full_name}")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('beneficiaries:detail', kwargs={'pk': self.kwargs['pk']})

class FamilyMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = FamilyMember
    form_class = FamilyMemberForm
    template_name = 'beneficiaries/family_member_form.html'

    def get_success_url(self):
        return reverse_lazy('beneficiaries:detail', kwargs={'pk': self.object.beneficiary.pk})

class FamilyMemberDeleteView(LoginRequiredMixin, DeleteView):
    model = FamilyMember
    template_name = 'beneficiaries/family_member_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('beneficiaries:detail', kwargs={'pk': self.object.beneficiary.pk})

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Family member removed.")
        return super().delete(request, *args, **kwargs)

class BeneficiaryListView(LoginRequiredMixin, ListView):
    model = Beneficiary
    template_name = 'beneficiaries/list.html'
    context_object_name = 'beneficiaries'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['categories'] = Category.objects.all()
        context['stats'] = {
            'high_priority': qs.filter(priority_level='HIGH').count(),
            'medium_priority': qs.filter(priority_level='MEDIUM').count(),
            'low_priority': qs.filter(priority_level='LOW').count(),
        }
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        priority = self.request.GET.get('priority')
        
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(household_number__icontains=search) |
                Q(claim_reference_number__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if priority:
            queryset = queryset.filter(priority_level=priority)
            
        return queryset.order_by('-priority_score')

class BeneficiaryCreateView(LoginRequiredMixin, CreateView):
    model = Beneficiary
    template_name = 'beneficiaries/form.html'
    fields = [
        'full_name', 'address', 'barangay', 'contact_number', 'birthdate', 
        'gender', 'age', 'household_number', 'family_member_count', 
        'children_count', 'elderly_count', 'pwd_count', 'employment_status', 
        'monthly_income', 'house_condition', 'category', 'valid_id_photo', 
        'beneficiary_photo'
    ]
    success_url = reverse_lazy('beneficiaries:list')

    def form_valid(self, form):
        # Duplicate detection
        full_name = form.cleaned_data.get('full_name')
        household_number = form.cleaned_data.get('household_number')
        
        if Beneficiary.objects.filter(full_name=full_name, household_number=household_number).exists():
            messages.warning(self.request, "A beneficiary with this name and household number already exists.")
            return self.form_invalid(form)
            
        messages.success(self.request, "Beneficiary registered successfully!")
        return super().form_valid(form)

class BeneficiaryDetailView(LoginRequiredMixin, DetailView):
    model = Beneficiary
    template_name = 'beneficiaries/detail.html'

class BeneficiaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficiary
    template_name = 'beneficiaries/form.html'
    fields = [
        'full_name', 'address', 'barangay', 'contact_number', 'birthdate',
        'gender', 'age', 'household_number', 'family_member_count',
        'children_count', 'elderly_count', 'pwd_count', 'employment_status',
        'monthly_income', 'house_condition', 'category', 'valid_id_photo',
        'beneficiary_photo'
    ]
    success_url = reverse_lazy('beneficiaries:list')

class BeneficiaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Beneficiary
    template_name = 'beneficiaries/confirm_delete.html'
    success_url = reverse_lazy('beneficiaries:list')
    
    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Beneficiary record has been deleted.")
        return super().delete(request, *args, **kwargs)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'beneficiaries/category_list.html'

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'beneficiaries/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('beneficiaries:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'beneficiaries/category_form.html'
    fields = '__all__'
    success_url = reverse_lazy('beneficiaries:category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'beneficiaries/category_confirm_delete.html'
    success_url = reverse_lazy('beneficiaries:category_list')

@login_required
def export_beneficiaries_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="beneficiaries_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'DAFAC #', 'Barangay', 'Contact', 'Priority', 'Claim Status'])
    
    beneficiaries = Beneficiary.objects.all()
    for b in beneficiaries:
        writer.writerow([b.full_name, b.dafac_number, b.barangay, b.contact_number, b.priority_level, b.claim_status])
        
    return response
