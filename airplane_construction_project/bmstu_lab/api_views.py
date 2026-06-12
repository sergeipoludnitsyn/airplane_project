from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie  # ← ПЕРЕНЕСТИ СЮДА
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.cache import SessionStore  # ← ДЛЯ ПРИНУДИТЕЛЬНОГО СОХРАНЕНИЯ
import os
import uuid

from .models import Airplane, Configuration, AirplaneConfiguration
from .serializers import (
    AirplaneSerializer, AirplaneCreateSerializer,
    ConfigurationListSerializer, ConfigurationDetailSerializer,
    ConfigurationUpdateSerializer, ConfigurationModerateSerializer,
    AirplaneConfigurationSerializer, CartIconSerializer,
    UserRegisterSerializer, UserLoginSerializer, SingletonUserSerializer,
    UserMeSerializer
)


# ==================== SINGLETON ФУНКЦИЯ (константный пользователь) ====================
def get_current_user():
    """
    Singleton-функция: всегда возвращает одного и того же пользователя.
    Используется во всех методах API как константа.
    """
    user, created = User.objects.get_or_create(
        username='const_airplane_user',
        defaults={'email': 'const@airplane.com', 'is_active': True}
    )
    if created:
        user.set_password('const_password_123')
        user.save()
    return user


def get_moderator_user():
    """Фиксированный модератор"""
    user, created = User.objects.get_or_create(
        username='const_moderator',
        defaults={'email': 'moderator@airplane.com', 'is_active': True, 'is_staff': True}
    )
    if created:
        user.set_password('moderator_123')
        user.save()
    return user


def save_file_to_minio(file, folder):
    """Сохранение файла в MinIO"""
    if not file:
        return None
    ext = os.path.splitext(file.name)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{folder}/{filename}"
    from django.core.files.storage import default_storage
    saved_path = default_storage.save(file_path, file)
    return f"{settings.MEDIA_URL}{saved_path}"


# ==================== 1. GET список самолётов (с фильтром) ====================
@api_view(['GET'])
def airplane_list(request):
    """GET /api/airplanes/ - список самолётов с фильтрацией"""
    get_current_user()  # демонстрация Singleton
    
    queryset = Airplane.objects.filter(status='active')
    
    # Фильтр по названию модели
    model_name = request.query_params.get('model_name')
    if model_name:
        queryset = queryset.filter(model_name__icontains=model_name)
    
    # Фильтр по цене
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    
    # Фильтр по производителю
    manufacturer = request.query_params.get('manufacturer')
    if manufacturer:
        queryset = queryset.filter(manufacturer__icontains=manufacturer)
    
    serializer = AirplaneSerializer(queryset, many=True)
    return Response(serializer.data)


# ==================== 1.5. GET детали одного самолёта ====================
@api_view(['GET'])
def airplane_detail(request, pk):
    """GET /api/airplanes/<pk>/ - детали одного комплектующего (видео, характеристики, цена)"""
    try:
        airplane = Airplane.objects.get(pk=pk, status='active')
    except Airplane.DoesNotExist:
        return Response({'error': 'Самолёт/комплектующее не найдено'}, status=404)
    
    serializer = AirplaneSerializer(airplane)
    return Response(serializer.data)


# ==================== 2. GET иконка корзины ====================
@api_view(['GET'])
def cart_icon(request):
    """GET /api/cart/icon/ - иконка корзины (ID черновика и кол-во)"""
    user = get_current_user()  # Singleton используется
    
    draft = Configuration.objects.filter(creator=user, status='draft').first()
    
    if not draft:
        return Response({'configuration_id': None, 'items_count': 0})
    
    items_count = draft.items.aggregate(total=Sum('quantity'))['total'] or 0
    return Response({'configuration_id': draft.id, 'items_count': items_count})


# ==================== 3. DELETE конфигурации (если есть) ====================
@api_view(['DELETE'])
def delete_configuration(request, pk):
    """DELETE /api/configurations/<pk>/delete/ - мягкое удаление черновика"""
    user = get_current_user()  # Singleton используется
    
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    # Только черновик может удалить создатель
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя удалить'}, status=403)
    
    config.status = 'deleted'
    config.save()
    
    return Response({'message': 'Конфигурация удалена', 'id': config.id})


# ==================== 5. POST добавить самолёт (с картинкой и видео) ====================
@api_view(['POST'])
def create_airplane(request):
    """POST /api/airplanes/create/ - добавить новый самолёт с изображением и видео"""
    data = request.data.copy()
    image_file = request.FILES.get('image_file')
    video_file = request.FILES.get('video_file')
    
    if image_file:
        data['image_url'] = save_file_to_minio(image_file, 'airplanes/images')
    if video_file:
        data['video_url'] = save_file_to_minio(video_file, 'airplanes/videos')
    
    serializer = AirplaneCreateSerializer(data=data)
    if serializer.is_valid():
        airplane = Airplane.objects.create(**serializer.validated_data, status='active')
        return Response(AirplaneSerializer(airplane).data, status=201)
    return Response(serializer.errors, status=400)


# ==================== 6. POST добавить самолёт в конфигурацию ====================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_airplane_to_configuration(request, config_id, airplane_id):
    """POST /api/configurations/<config_id>/add-airplane/<airplane_id>/"""
    user = request.user  # Берем текущего авторизованного пользователя
    
    try:
        config = Configuration.objects.get(pk=config_id)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    # Проверка прав (только свой черновик)
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя редактировать'}, status=403)
    
    try:
        airplane = Airplane.objects.get(pk=airplane_id, status='active')
    except Airplane.DoesNotExist:
        return Response({'error': 'Самолёт не найден'}, status=404)
    
    quantity = int(request.data.get('quantity', 1))
    
    # Добавляем или обновляем позицию
    item, created = AirplaneConfiguration.objects.get_or_create(
        configuration=config,
        airplane=airplane,
        defaults={'quantity': quantity, 'order_index': config.items.count()}
    )
    
    if not created:
        item.quantity += quantity
        item.save()
    
    serializer = AirplaneConfigurationSerializer(item)
    return Response(serializer.data, status=201)


# ==================== 9. GET посмотреть конфигурацию ====================
@api_view(['GET'])
def configuration_detail(request, pk):
    """GET /api/configurations/<pk>/ - детали конфигурации со всеми самолётами"""
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    if config.status == 'deleted':
        return Response({'error': 'Конфигурация удалена'}, status=404)
    
    serializer = ConfigurationDetailSerializer(config)
    return Response(serializer.data)


# ==================== 10. PATCH изменить поле м-м (mm_field) ====================
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_mm_field(request, pk):
    """PATCH /api/configurations/<pk>/mm-field/ - изменить поле mm_field"""
    user = request.user
    
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя редактировать'}, status=403)
    
    mm_field_value = request.data.get('mm_field')
    if mm_field_value is not None:
        config.mm_field = mm_field_value
        config.save()
    
    return Response(ConfigurationDetailSerializer(config).data)


# ==================== 11. PUT изменить конфигурацию ====================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_configuration(request, pk):
    """PUT /api/configurations/<pk>/update/ - изменить customer_name и другие поля"""
    user = request.user
    
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя редактировать'}, status=403)
    
    serializer = ConfigurationUpdateSerializer(config, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(ConfigurationDetailSerializer(config).data)
    return Response(serializer.errors, status=400)


# ==================== 12. POST завершить конфигурацию (только для модераторов) ====================
@api_view(['POST'])
@permission_classes([IsAdminUser])
def complete_configuration(request, pk):
    """POST /api/configurations/<pk>/complete/ - завершить (только для модераторов, статус должен быть 'formed')"""
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    # Проверка: можно завершить только сформированную
    if config.status != 'formed':
        return Response({'error': f'Нельзя завершить. Текущий статус: {config.status}. Сначала сформируйте заявку (status должен быть "formed")'}, 
                        status=400)
    
    moderator = request.user
    config.status = 'completed'
    config.completed_at = timezone.now()
    config.moderator = moderator
    config.save()
    
    return Response({'id': config.id, 'status': config.status, 'message': 'Конфигурация завершена'})


# ==================== 13. POST сформировать конфигурацию (расчёт стоимости) ====================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_configuration(request, pk):
    """POST /api/configurations/<pk>/finalize/ - сформировать с расчётом стоимости"""
    user = request.user
    
    try:
        config = Configuration.objects.get(pk=pk)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    # Проверка прав: только черновик может сформировать создатель
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя сформировать'}, status=403)
    
    # Проверка обязательных полей
    if not config.customer_name or config.customer_name == 'Гость':
        return Response({'error': 'Заполните customer_name'}, status=400)
    
    if config.items.count() == 0:
        return Response({'error': 'Нет самолётов в конфигурации'}, status=400)
    
    # ========== РАСЧЁТ СТОИМОСТИ ==========
    total = 0
    
    for item in config.items.all():
        item_price = float(item.airplane.price)
        item_total = item.quantity * item_price
        total += item_total
    
    # Сохраняем в конфигурацию
    config.status = 'formed'
    config.formed_at = timezone.now()
    config.save()
    
    delivery_date = timezone.now() + timezone.timedelta(days=45)
    
    return Response({
        'id': config.id,
        'status': config.status,
        'formed_at': config.formed_at,
        'total_cost': total,
        'delivery_date': delivery_date,
        'message': 'Конфигурация успешно сформирована'
    })


# ==================== 15. POST зарегистрировать пользователя ====================
@api_view(['POST'])
def register_user(request):
    """POST /api/users/register/ - регистрация пользователя"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        const_user = get_current_user()
        return Response({
            'new_user': {'id': user.id, 'username': user.username},
            'singleton_user': {'id': const_user.id, 'username': const_user.username},
            'message': 'Пользователь зарегистрирован, но в API используется Singleton-константа'
        }, status=201)
    return Response(serializer.errors, status=400)


# ==================== 16. GET показать изменённые данные через SELECT ====================
@api_view(['GET'])
def configuration_statuses_select(request):
    """GET /api/configurations/statuses/ - SELECT DISTINCT статусов конфигураций"""
    user = get_current_user()
    
    statuses = Configuration.objects.values_list('status', flat=True).distinct()
    
    status_counts = {}
    for status_code, status_name in Configuration.STATUS_CHOICES:
        count = Configuration.objects.filter(status=status_code).count()
        status_counts[status_code] = {
            'name': status_name,
            'count': count
        }
    
    return Response({
        'available_statuses': dict(Configuration.STATUS_CHOICES),
        'distinct_statuses': list(statuses),
        'status_counts': status_counts,
        'singleton_user_used': user.username
    })


# ==================== GET список конфигураций (с правами доступа) ====================
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def configuration_list(request):
    """GET /api/configurations/ - список конфигураций (без черновиков и удалённых) с фильтрацией"""
    
    # Проверка авторизации
    if not request.user.is_authenticated:
        return Response({'error': 'Требуется авторизация'}, status=401)
    
    user = request.user
    
    queryset = Configuration.objects.exclude(status__in=['draft', 'deleted'])
    
    if not user.is_staff:
        queryset = queryset.filter(creator=user)
    
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    date_from = request.query_params.get('formed_from')
    date_to = request.query_params.get('formed_to')
    if date_from:
        queryset = queryset.filter(formed_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(formed_at__date__lte=date_to)
    
    customer = request.query_params.get('customer_name')
    if customer:
        queryset = queryset.filter(customer_name__icontains=customer)
    
    serializer = ConfigurationListSerializer(queryset, many=True)
    return Response(serializer.data)


# ==================== ДОПОЛНИТЕЛЬНО: удалить позицию из конфигурации ====================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_airplane_from_configuration(request, config_id, airplane_id):
    """DELETE /api/configurations/<config_id>/remove-airplane/<airplane_id>/"""
    user = request.user
    
    try:
        config = Configuration.objects.get(pk=config_id)
    except Configuration.DoesNotExist:
        return Response({'error': 'Конфигурация не найдена'}, status=404)
    
    if config.status != 'draft' or config.creator != user:
        return Response({'error': 'Нельзя редактировать'}, status=403)
    
    try:
        item = AirplaneConfiguration.objects.get(configuration=config, airplane_id=airplane_id)
    except AirplaneConfiguration.DoesNotExist:
        return Response({'error': 'Позиция не найдена'}, status=404)
    
    item.delete()
    return Response({'message': 'Самолёт удалён из конфигурации'})


# ==================== АУТЕНТИФИКАЦИЯ ====================

@api_view(['POST'])
@permission_classes([])
@csrf_exempt
@ensure_csrf_cookie
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Требуются username и password'}, status=400)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        # ПРИНУДИТЕЛЬНОЕ СОХРАНЕНИЕ СЕССИИ
        request.session.save()
        print(f"Session key: {request.session.session_key}")
        print(f"Session data: {request.session.items()}")
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'message': 'Вход выполнен успешно'
        })
    else:
        return Response({'error': 'Неверное имя пользователя или пароль'}, status=401)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """POST /api/users/logout/ - деавторизация"""
    logout(request)
    return Response({'message': 'Выход выполнен успешно'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    """GET /api/users/me/ - текущий пользователь"""
    serializer = UserMeSerializer(request.user)
    return Response(serializer.data)