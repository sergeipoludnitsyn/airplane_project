# urls.py
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.airplane_list, name='airplane_list'),
    
    # Детальная страница комплектующей
    path('part/<int:part_id>/', views.aircraft_part_detail, name='aircraft_part_detail'),
    
    # Страница оформления заявки - ИЗМЕНЕНО: order -> request
    path('request/', views.order_request, name='order_request'),
]