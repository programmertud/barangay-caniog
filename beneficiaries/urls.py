from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    path('', views.BeneficiaryListView.as_view(), name='list'),
    path('add/', views.BeneficiaryCreateView.as_view(), name='add'),
    path('<int:pk>/', views.BeneficiaryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BeneficiaryUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BeneficiaryDeleteView.as_view(), name='delete'),
    path('<int:pk>/family/add/', views.FamilyMemberCreateView.as_view(), name='family_add'),
    path('family/<int:pk>/edit/', views.FamilyMemberUpdateView.as_view(), name='family_edit'),
    path('family/<int:pk>/delete/', views.FamilyMemberDeleteView.as_view(), name='family_delete'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('export/csv/', views.export_beneficiaries_csv, name='export_csv'),
]
