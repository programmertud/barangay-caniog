from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ActivityLog

class ActivityLogListView(LoginRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'logs/list.html'
    context_object_name = 'logs'
    paginate_by = 20

    def get_queryset(self):
        return ActivityLog.objects.all().order_by('-timestamp')
