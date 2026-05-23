from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # ========== HTML страницы (лабораторная 2) ==========
    path('', views.service_list, name='airplane_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('request/', views.order_request, name='order_request'),
    path('add-to-order/<int:product_id>/', views.add_to_order, name='add_to_order'),
    path('delete-order/<int:order_id>/', views.delete_order_sql, name='delete_order_sql'),
    
    # ========== API (лабораторная 3) ==========
    
    # Домен: Услуги (AirplaneProduct)
    path('api/services/', api_views.product_list, name='api_product_list'),
    path('api/services/<int:pk>/', api_views.product_detail, name='api_product_detail'),
    path('api/services/create/', api_views.product_create, name='api_product_create'),
    
    # Домен: Корзина
    path('api/cart/icon/', api_views.cart_icon, name='api_cart_icon'),
    
    # Домен: Заявки (AirplaneRequest)
    path('api/requests/', api_views.request_list, name='api_request_list'),
    path('api/requests/<int:pk>/', api_views.request_detail, name='api_request_detail'),
    path('api/requests/<int:pk>/update/', api_views.request_update, name='api_request_update'),
    path('api/requests/<int:pk>/form/', api_views.request_form, name='api_request_form'),
    path('api/requests/<int:pk>/complete/', api_views.request_moderate, name='api_request_moderate'),  # переименовал
    path('api/requests/<int:pk>/delete/', api_views.request_delete, name='api_request_delete'),
    
    # Домен: Связь м-м (AirplaneRequestItem) - БЕЗ PK в URL!
    path('api/request-items/add/<int:product_id>/', api_views.request_item_add, name='api_request_item_add'),
    path('api/request-items/update/', api_views.request_item_update, name='api_request_item_update'),  # без PK
    path('api/request-items/delete/', api_views.request_item_delete, name='api_request_item_delete'),  # без PK
    
    # Домен: Пользователи
    path('api/users/register/', api_views.user_register, name='api_user_register'),
    path('api/users/login/', api_views.user_login, name='api_user_login'),
    path('api/users/logout/', api_views.user_logout, name='api_user_logout'),
]