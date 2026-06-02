from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportsHomeView.as_view(), name='home'),
    path('export/beneficiaries/', views.export_beneficiaries_excel, name='export_beneficiaries'),
    path('export/inventory/', views.export_inventory_excel, name='export_inventory'),
    path('export/dromic/', views.export_dromic_report, name='export_dromic'),
]
