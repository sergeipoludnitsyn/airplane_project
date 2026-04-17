from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.airplane_list, name='airplane_list'),
    path('part/<int:part_id>/', views.aircraft_part_detail, name='aircraft_part_detail'),
    path('request/', views.order_request, name='order_request'),
    path('add-to-cart/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete-order/', views.delete_current_order, name='delete_current_order'),
    
    # Добавить страницы входа и выхода
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]