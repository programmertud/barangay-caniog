from django.urls import path
from . import views

app_name = 'distribution'

urlpatterns = [
    path('', views.DistributionListView.as_view(), name='list'),
    path('add/', views.DistributionCreateView.as_view(), name='add'),
    path('<int:pk>/', views.DistributionDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.DistributionUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DistributionDeleteView.as_view(), name='delete'),
    path('verify/', views.verify_qr, name='verify'),
]
