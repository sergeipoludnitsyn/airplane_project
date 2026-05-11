from django.urls import path
from . import views
from . import api_views

app_name = 'bmstu_lab'

urlpatterns = [
    path('', views.service_list, name='airplane_list'),
    path('product/<int:service_id>/', views.product_detail, name='product_detail'),
    path('request/', views.order_request, name='order_request'),
    path('request/<int:order_id>/', views.order_request, name='order_request_by_id'),
    path('add-to-order/<int:service_id>/', views.add_to_order, name='add_to_order'),
    path('delete-order/<int:order_id>/', views.delete_order_sql, name='delete_order_sql'),  # ОДИН РАЗ
    
    # API
    path('api/services/', api_views.service_list, name='api_service_list'),
    path('api/services/<int:pk>/', api_views.service_detail, name='api_service_detail'),
    path('api/services/create/', api_views.service_create, name='api_service_create'),
    path('api/orders/<int:order_id>/services/<int:service_id>/', 
         api_views.order_service_delete, name='api_order_service_delete'),
    path('api/orders/<int:order_id>/services/<int:service_id>/update/', 
         api_views.order_service_update, name='api_order_service_update'),
    path('api/orders/services/<int:service_id>/add/', 
         api_views.order_service_add, name='api_order_service_add'),
    path('api/cart/icon/', api_views.cart_icon, name='api_cart_icon'),
    path('api/orders/', api_views.order_list, name='api_order_list'),
    path('api/orders/<int:pk>/', api_views.order_detail, name='api_order_detail'),
    path('api/orders/<int:pk>/update/', api_views.order_update, name='api_order_update'),
    path('api/orders/<int:pk>/form/', api_views.order_form, name='api_order_form'),
    path('api/orders/<int:pk>/moderate/', api_views.order_moderate, name='api_order_moderate'),
    path('api/orders/<int:pk>/delete/', api_views.order_delete, name='api_order_delete'),
    path('api/users/register/', api_views.user_register, name='api_user_register'),
    path('api/users/login/', api_views.user_login, name='api_user_login'),
    path('api/users/logout/', api_views.user_logout, name='api_user_logout'),
]