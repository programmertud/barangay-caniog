from django.urls import path
from . import views, kit_views

app_name = 'inventory'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='list'),
    path('add/', views.ItemCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ItemDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ItemUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='delete'),
    path('kits/', views.KitListView.as_view(), name='kit_list'),
    path('kits/add/', views.KitCreateView.as_view(), name='kit_create'),
    path('kits/<int:pk>/', views.KitDetailView.as_view(), name='kit_detail'),
    path('kits/<int:pk>/edit/', views.KitUpdateView.as_view(), name='kit_edit'),
    path('kits/<int:pk>/delete/', views.KitDeleteView.as_view(), name='kit_delete'),
    path('kits/<int:pk>/assemble/', kit_views.kit_assemble, name='kit_assemble'),
    path('kits/<int:kit_pk>/remove-item/<int:item_pk>/', kit_views.kit_remove_item, name='kit_remove_item'),
]
