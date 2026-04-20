from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.airplane_list, name='airplane_list'),
    path('part/<int:part_id>/', views.aircraft_part_detail, name='aircraft_part_detail'),
    path('request/', views.order_request, name='order_request'),
    path('add-to-cart/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete-order/', views.delete_current_order, name='delete_current_order'),
    
    path('request/<int:order_id>/', views.order_detail, name='order_detail'),
]