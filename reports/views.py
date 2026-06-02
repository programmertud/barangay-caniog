from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db import models
from beneficiaries.models import Beneficiary
from inventory.models import Item
from distribution.models import Distribution
from events.models import ReliefEvent
import pandas as pd
from io import BytesIO

class ReportsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_beneficiaries'] = Beneficiary.objects.count()
        context['total_distributions'] = Distribution.objects.count()
        context['total_events'] = ReliefEvent.objects.count()
        context['total_low_stock'] = Item.objects.filter(stock_quantity__lte=models.F('low_stock_threshold')).count()
        
        # Priority Stats
        context['high_priority'] = Beneficiary.objects.filter(priority_level='HIGH').count()
        context['medium_priority'] = Beneficiary.objects.filter(priority_level='MEDIUM').count()
        context['low_priority'] = Beneficiary.objects.filter(priority_level='LOW').count()
        
        return context

def export_beneficiaries_excel(request):
    beneficiaries = Beneficiary.objects.all().values(
        'full_name', 'household_number', 'priority_level', 'priority_score', 'claim_status', 'barangay'
    )
    df = pd.DataFrame(list(beneficiaries))
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Beneficiaries')
    
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=beneficiaries_report.xlsx'
    return response

def export_inventory_excel(request):
    items = Item.objects.all().values('name', 'category', 'stock_quantity', 'unit', 'low_stock_threshold')
    df = pd.DataFrame(list(items))
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventory')
    
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=inventory_report.xlsx'
    return response

def export_dromic_report(request):
    """
    Generates a DROMIC-style report summarizing affected population demographics.
    """
    beneficiaries = Beneficiary.objects.all()
    
    data = []
    for b in beneficiaries:
        # Each beneficiary represents one family
        family_members = b.family_members.all()
        
        # Calculate vulnerabilities for the whole household
        pregnant_count = family_members.filter(is_pregnant=True).count()
        lactating_count = family_members.filter(is_lactating_mother=True).count()
        pwd_count = b.pwd_count
        elderly_count = b.elderly_count
        children_count = b.children_count
        
        data.append({
            'Barangay': b.barangay,
            'Families': 1,
            'Persons': b.family_member_count,
            'Children (<18)': children_count,
            'Elderly (60+)': elderly_count,
            'PWDs': pwd_count,
            'Pregnant': pregnant_count,
            'Lactating Mothers': lactating_count,
        })
    
    df = pd.DataFrame(data)
    
    # Aggregate by Barangay
    summary_df = df.groupby('Barangay').sum().reset_index()
    
    # Add Total Row
    total_row = summary_df.select_dtypes(include=['number']).sum()
    total_row['Barangay'] = 'GRAND TOTAL'
    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='DROMIC Report')
        
        # Add a sheet for detailed demographics
        df.to_excel(writer, index=False, sheet_name='Detailed List')
    
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=DROMIC_Report_{pd.Timestamp.now().strftime("%Y%m%d")}.xlsx'
    return response
