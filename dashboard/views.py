from django.db.models import Sum, F, Count
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from beneficiaries.models import Beneficiary
from inventory.models import Item
from events.models import ReliefEvent
from distribution.models import Distribution
from logs.models import ActivityLog

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_beneficiaries'] = Beneficiary.objects.count()
        context['high_priority'] = Beneficiary.objects.filter(priority_level='HIGH').count()
        context['ongoing_events'] = ReliefEvent.objects.filter(status='ONGOING').count()
        context['planned_events'] = ReliefEvent.objects.filter(status='PLANNED').count()
        context['cancelled_events'] = ReliefEvent.objects.filter(status='CANCELLED').count()
        context['total_items'] = Item.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0
        context['low_stock_items'] = Item.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count()
        
        # Recent distributions
        context['recent_distributions'] = Distribution.objects.all().order_by('-timestamp')[:5]
        
        # Recent logs
        context['recent_activities'] = ActivityLog.objects.all().order_by('-timestamp')[:5]
        
        # Chart Data: Distributions per day for the last 7 days
        today = timezone.localtime(timezone.now()).date()
        chart_labels = []
        chart_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Distribution.objects.filter(timestamp__date=day).count()
            chart_labels.append(day.strftime('%a'))
            chart_data.append(count)
        
        context['chart_labels'] = chart_labels
        context['chart_data'] = chart_data
        
        return context

from django.http import JsonResponse
from django.db.models import Q
import json

def ai_assistant_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').lower()
            
            response = "I'm sorry, I couldn't find a specific answer for that. Could you try asking about 'stock', 'beneficiaries', or 'events'?"
            
            # Expanded Keyword Matching
            is_stock = any(word in query for word in ['stock', 'item', 'inventory', 'supply', 'kit', 'bundle'])
            is_beneficiary = any(word in query for word in ['beneficiar', 'people', 'record', 'person', 'family', 'household', 'resident'])
            is_event = any(word in query for word in ['event', 'relief', 'ongoing', 'planned', 'distribution', 'operation'])

            if is_stock:
                total_items = Item.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0
                low_stock = Item.objects.filter(stock_quantity__lte=F('low_stock_threshold')).count()
                response = f"Your current inventory has a total of {total_items} items. I noticed that {low_stock} items are currently at low-stock levels."
                
            elif is_beneficiary:
                total = Beneficiary.objects.count()
                high = Beneficiary.objects.filter(priority_level='HIGH').count()
                response = f"You have {total} total beneficiaries registered in the system. Of these, {high} are High Priority."
                
            elif is_event:
                ongoing = ReliefEvent.objects.filter(status='ONGOING').count()
                planned = ReliefEvent.objects.filter(status='PLANNED').count()
                response = f"Currently, there are {ongoing} relief events ongoing and {planned} events planned in your calendar."

            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)
