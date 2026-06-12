from django.urls import path
from . import api_views

urlpatterns = [
    # Продукты
    path('api/products/', api_views.product_list, name='api_product_list'),
    path('api/products/<int:pk>/', api_views.product_detail, name='api_product_detail'),
    path('api/products/create/', api_views.product_create, name='api_product_create'),
    # Иконка корзины
    path('api/cart/icon/', api_views.cart_icon, name='api_cart_icon'),
    # Заявки
    path('api/requests/', api_views.request_list, name='api_request_list'),
    path('api/requests/<int:pk>/', api_views.request_detail, name='api_request_detail'),
    path('api/requests/<int:pk>/update/', api_views.request_update, name='api_request_update'),
    path('api/requests/<int:pk>/form/', api_views.request_form, name='api_request_form'),
    path('api/requests/<int:pk>/moderate/', api_views.request_moderate, name='api_request_moderate'),
    path('api/requests/<int:pk>/delete/', api_views.request_delete, name='api_request_delete'),
    # Позиции
    path('api/requests/items/add/<int:product_id>/', api_views.request_item_add, name='api_request_item_add'),
    path('api/requests/<int:request_id>/items/<int:item_id>/update/', api_views.request_item_update, name='api_request_item_update'),
    path('api/requests/<int:request_id>/items/<int:item_id>/', api_views.request_item_delete, name='api_request_item_delete'),
    # Пользователи
    path('api/users/register/', api_views.user_register, name='api_user_register'),
    path('api/users/login/', api_views.user_login, name='api_user_login'),
    path('api/users/logout/', api_views.user_logout, name='api_user_logout'),
]