from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # ========== HTML страницы ==========
    path('', views.airplane_list_html, name='airplane_list_html'),
    path('airplane/<int:airplane_id>/', views.airplane_detail_html, name='airplane_detail_html'),
    path('configuration/', views.configuration_html, name='configuration_html'),
    path('add-to-configuration/<int:airplane_id>/', views.add_to_configuration, name='add_to_configuration'),
    path('delete-configuration/<int:config_id>/', views.delete_configuration_sql, name='delete_configuration_sql'),
    
    # ========== API (16 методов для Insomnia) ==========
    
    # 1. GET список самолётов с фильтром
    path('api/airplanes/', api_views.airplane_list, name='api_airplane_list'),
    
    # 2. GET иконка корзины
    path('api/cart/icon/', api_views.cart_icon, name='api_cart_icon'),
    
    # 3. DELETE конфигурации
    path('api/configurations/<int:pk>/delete/', api_views.delete_configuration, name='api_delete_configuration'),
    
    # 4. GET список самолётов с фильтром (тот же, что #1)
    
    # 5. POST создать самолёт
    path('api/airplanes/create/', api_views.create_airplane, name='api_create_airplane'),
    
    # 6,7. POST добавить самолёт в конфигурацию
    path('api/configurations/<int:config_id>/add-airplane/<int:airplane_id>/', 
         api_views.add_airplane_to_configuration, name='api_add_airplane'),
    
    # 8. GET иконка корзины (повторно) - см. #2
    
    # 9. GET детали конфигурации
    path('api/configurations/<int:pk>/', api_views.configuration_detail, name='api_configuration_detail'),
    
    # 10. PATCH изменить поле mm_field
    path('api/configurations/<int:pk>/mm-field/', api_views.update_mm_field, name='api_update_mm_field'),
    
    # 11. PUT изменить конфигурацию
    path('api/configurations/<int:pk>/update/', api_views.update_configuration, name='api_update_configuration'),
    
    # 12. POST завершить конфигурацию (с ошибкой если не сформирована)
    path('api/configurations/<int:pk>/complete/', api_views.complete_configuration, name='api_complete_configuration'),
    
    # 13. POST сформировать конфигурацию (расчёт стоимости)
    path('api/configurations/<int:pk>/finalize/', api_views.finalize_configuration, name='api_finalize_configuration'),
    
    # 14. POST завершить сформированную - см. #12
    
    # 15. POST регистрация пользователя
    path('api/users/register/', api_views.register_user, name='api_register_user'),
    
    # 16. GET статусы (SELECT)
    path('api/configurations/statuses/', api_views.configuration_statuses_select, name='api_statuses_select'),
    
    # Дополнительно: список конфигураций с фильтрацией
    path('api/configurations/', api_views.configuration_list, name='api_configuration_list'),
    
    # Удаление позиции
    path('api/configurations/<int:config_id>/remove-airplane/<int:airplane_id>/', 
         api_views.remove_airplane_from_configuration, name='api_remove_airplane'),
    
    # ========== АУТЕНТИФИКАЦИЯ (НОВЫЕ МАРШРУТЫ) ==========
    path('api/users/login/', api_views.user_login, name='api_user_login'),
    path('api/users/logout/', api_views.user_logout, name='api_user_logout'),
    path('api/users/me/', api_views.user_me, name='api_user_me'),
]