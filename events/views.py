from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ReliefEvent

class EventListView(LoginRequiredMixin, ListView):
    model = ReliefEvent
    template_name = 'events/list.html'
    context_object_name = 'events'

class EventCreateView(LoginRequiredMixin, CreateView):
    model = ReliefEvent
    template_name = 'events/form.html'
    fields = ['title', 'description', 'event_type', 'location', 'start_date', 'status']
    success_url = reverse_lazy('events:list')

class EventDetailView(LoginRequiredMixin, DetailView):
    model = ReliefEvent
    template_name = 'events/detail.html'
    context_object_name = 'event'

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = ReliefEvent
    template_name = 'events/form.html'
    fields = ['title', 'description', 'event_type', 'location', 'start_date', 'status']
    success_url = reverse_lazy('events:list')

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = ReliefEvent
    template_name = 'events/confirm_delete.html'
    success_url = reverse_lazy('events:list')
