from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('create/', views.category_create, name='category_create'),
    path('edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('api/list/', views.category_api_list, name='category_api_list'),
    path('api/create/', views.category_create_ajax, name='category_create_ajax'),
]