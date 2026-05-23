from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
import os
import uuid

from .models import AirplaneProduct, AirplaneRequest, AirplaneRequestItem
from .serializers import (
    AirplaneProductSerializer, AirplaneProductCreateSerializer,
    AirplaneRequestListSerializer, AirplaneRequestDetailSerializer,
    AirplaneRequestUpdateSerializer, AirplaneRequestFormSerializer, AirplaneRequestModerateSerializer,
    AirplaneRequestItemSerializer, CartIconSerializer,
    UserRegisterSerializer, UserLoginSerializer, UserLogoutSerializer
)
from django.contrib.auth.models import User


def get_current_user():
    """Фиксированный пользователь-создатель (константа)"""
    user, created = User.objects.get_or_create(
        username='api_user',
        defaults={'email': 'api@example.com', 'is_active': True}
    )
    if created:
        user.set_password('api_password_123')
        user.save()
    return user


def get_moderator_user():
    """Фиксированный модератор"""
    user, created = User.objects.get_or_create(
        username='moderator',
        defaults={'email': 'moderator@example.com', 'is_active': True, 'is_staff': True}
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


# ==================== ДОМЕН: УСЛУГИ (AirplaneProduct) ====================

@api_view(['GET'])
def product_list(request):
    """GET список услуг с фильтрацией"""
    queryset = AirplaneProduct.objects.filter(status='active')
    
    # Фильтрация по названию
    name = request.query_params.get('name')
    if name:
        queryset = queryset.filter(name__icontains=name)
    
    serializer = AirplaneProductSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, pk):
    """GET одна услуга"""
    try:
        product = AirplaneProduct.objects.get(pk=pk, status='active')
    except AirplaneProduct.DoesNotExist:
        return Response({'error': 'Продукт не найден'}, status=404)
    
    serializer = AirplaneProductSerializer(product)
    return Response(serializer.data)


@api_view(['POST'])
def product_create(request):
    """POST добавление услуги + файлы изображения и видео"""
    data = request.data.copy()
    image_file = request.FILES.get('image_file')
    video_file = request.FILES.get('video_file')
    
    if image_file:
        data['image_url'] = save_file_to_minio(image_file, 'products/images')
    if video_file:
        data['video_url'] = save_file_to_minio(video_file, 'products/videos')
    
    serializer = AirplaneProductCreateSerializer(data=data)
    if serializer.is_valid():
        serializer.save(status='active')
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ==================== ДОМЕН: КОРЗИНА ====================

@api_view(['GET'])
def cart_icon(request):
    """GET иконка корзины - id черновика и количество услуг"""
    user = get_current_user()
    draft = AirplaneRequest.objects.filter(creator=user, status='draft').first()
    
    if not draft:
        return Response({'request_id': None, 'items_count': 0})
    
    items_count = draft.items.aggregate(total=Sum('quantity'))['total'] or 0
    return Response({'request_id': draft.id, 'items_count': items_count})


# ==================== ДОМЕН: ЗАЯВКИ (AirplaneRequest) ====================

@api_view(['GET'])
def request_list(request):
    """GET список заявок (без черновиков и удаленных) с фильтрацией"""
    queryset = AirplaneRequest.objects.exclude(status__in=['draft', 'deleted'])
    
    # Фильтр по статусу
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Фильтр по диапазону дат формирования
    date_from = request.query_params.get('formed_from')
    date_to = request.query_params.get('formed_to')
    if date_from:
        queryset = queryset.filter(formed_at__gte=date_from)
    if date_to:
        queryset = queryset.filter(formed_at__lte=date_to)
    
    serializer = AirplaneRequestListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def request_detail(request, pk):
    """GET одна заявка + её услуги"""
    try:
        req = AirplaneRequest.objects.get(pk=pk)
    except AirplaneRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
    
    if req.status == 'deleted':
        return Response({'error': 'Заявка удалена'}, status=404)
    
    serializer = AirplaneRequestDetailSerializer(req)
    return Response(serializer.data)


@api_view(['PUT'])
def request_update(request, pk):
    """PUT изменение полей заявки (тема, адрес и т.д.)"""
    try:
        req = AirplaneRequest.objects.get(pk=pk)
    except AirplaneRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
    
    user = get_current_user()
    
    # Только черновик может редактировать создатель
    if req.status != 'draft' or req.creator != user:
        return Response({'error': 'Нельзя редактировать'}, status=403)
    
    serializer = AirplaneRequestUpdateSerializer(req, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
def request_form(request, pk):
    """PUT сформировать заявку (расчет стоимости, даты доставки, вычисления в м-м)"""
    try:
        req = AirplaneRequest.objects.get(pk=pk)
    except AirplaneRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
    
    user = get_current_user()
    
    # Проверка прав
    if req.status != 'draft' or req.creator != user:
        return Response({'error': 'Нельзя сформировать'}, status=403)
    
    # Проверка обязательных полей
    required_fields = ['client_name', 'purpose', 'aircraft_model']
    missing_fields = []
    for field in required_fields:
        value = getattr(req, field, None)
        if not value or value == 'Гость':
            missing_fields.append(field)
    
    if missing_fields:
        return Response({
            'error': f'Заполните обязательные поля: {", ".join(missing_fields)}'
        }, status=400)
    
    if req.items.count() == 0:
        return Response({'error': 'Нет продуктов в заявке'}, status=400)
    
    # ========== РАСЧЕТ СТОИМОСТИ И ВЫЧИСЛЕНИЙ В М-М ==========
    total = 0
    delivery_cost = 0
    
    for item in req.items.all():
        item_price = float(item.product.price)
        item_total = item.quantity * item_price
        total += item_total
        
        # Вычисление в м-м (лабораторная 8)
        # Пример расчета в зависимости от веса продукта
        weight = float(item.product.weight)
        
        if weight > 100:
            # Наценка за тяжелый груз
            extra_charge = item_total * 0.1
            item.result_field = f"Наценка за вес ({weight}кг): +{extra_charge:.2f} ₽"
            total += extra_charge
            delivery_cost += extra_charge
        elif weight > 50:
            extra_charge = item_total * 0.05
            item.result_field = f"Наценка за вес ({weight}кг): +{extra_charge:.2f} ₽"
            total += extra_charge
            delivery_cost += extra_charge
        elif item.quantity >= 10:
            discount = item_total * 0.05
            item.result_field = f"Скидка 5% за опт: -{discount:.2f} ₽"
            total -= discount
        else:
            item.result_field = f"Стандартная цена: {item_total:.2f} ₽"
        
        item.save()
    
    # Расчет стоимости доставки
    if delivery_cost == 0:
        delivery_cost = total * 0.02  # 2% от стоимости если нет наценок
    
    # Дата доставки (в течении месяца)
    delivery_date = timezone.now() + timezone.timedelta(days=30)
    
    # Сохраняем в заявку
    req.total_cost = total
    req.delivery_price = delivery_cost
    req.status = 'formed'
    req.formed_at = timezone.now()
    req.save()
    
    return Response({
        'id': req.id,
        'status': req.status,
        'formed_at': req.formed_at,
        'total_cost': total,
        'delivery_price': delivery_cost,
        'delivery_date': delivery_date,
        'message': 'Заявка успешно сформирована'
    })


@api_view(['PUT'])
def request_moderate(request, pk):
    """PUT завершить/отклонить заявку (модератором)"""
    try:
        req = AirplaneRequest.objects.get(pk=pk)
    except AirplaneRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
    
    # Проверка статуса
    if req.status != 'formed':
        return Response({'error': 'Можно модернировать только сформированные заявки'}, status=400)
    
    serializer = AirplaneRequestModerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    action = serializer.validated_data['action']
    moderator = get_moderator_user()
    
    if action == 'complete':
        req.status = 'completed'
        req.completed_at = timezone.now()
        req.moderator = moderator
        req.save()
        
        return Response({
            'id': req.id,
            'status': req.status,
            'completed_at': req.completed_at,
            'message': 'Заявка успешно завершена'
        })
    
    elif action == 'reject':
        req.status = 'rejected'
        req.completed_at = timezone.now()
        req.moderator = moderator
        req.save()
        
        return Response({
            'id': req.id,
            'status': req.status,
            'completed_at': req.completed_at,
            'message': 'Заявка отклонена'
        })
    
    return Response({'error': 'Неизвестное действие. Используйте "complete" или "reject"'}, status=400)


@api_view(['DELETE'])
def request_delete(request, pk):
    """DELETE удаление заявки (мягкое - статус deleted)"""
    try:
        req = AirplaneRequest.objects.get(pk=pk)
    except AirplaneRequest.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=404)
    
    user = get_current_user()
    
    # Только черновик может удалить создатель
    if req.status != 'draft' or req.creator != user:
        return Response({'error': 'Нельзя удалить'}, status=403)
    
    req.status = 'deleted'
    req.save()
    
    return Response({'message': 'Заявка удалена', 'id': req.id})


# ==================== ДОМЕН: СВЯЗЬ М-М (AirplaneRequestItem) ====================

@api_view(['POST'])
def request_item_add(request, product_id):
    """POST добавить услугу в заявку-черновик"""
    user = get_current_user()
    
    # Получаем или создаем черновик
    draft, created = AirplaneRequest.objects.get_or_create(
        creator=user, 
        status='draft',
        defaults={
            'status': 'draft', 
            'client_name': 'Гость',
            'purpose': '',
            'aircraft_model': ''
        }
    )
    
    # Проверяем существование продукта
    try:
        product = AirplaneProduct.objects.get(id=product_id, status='active')
    except AirplaneProduct.DoesNotExist:
        return Response({'error': 'Продукт не найден'}, status=404)
    
    quantity = int(request.data.get('quantity', 1))
    
    # Добавляем или обновляем позицию
    item, created = AirplaneRequestItem.objects.get_or_create(
        request=draft, 
        product=product,
        defaults={'quantity': quantity, 'order': draft.items.count()}
    )
    
    if not created:
        item.quantity += quantity
        item.save()
    
    serializer = AirplaneRequestItemSerializer(item)
    return Response(serializer.data, status=201)


@api_view(['PUT'])
def request_item_update(request):
    """PUT изменение количества/порядка в м-м (без PK м-м)"""
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')
    order = request.data.get('order')
    
    if not product_id:
        return Response({'error': 'Не указан product_id'}, status=400)
    
    user = get_current_user()
    draft = AirplaneRequest.objects.filter(creator=user, status='draft').first()
    
    if not draft:
        return Response({'error': 'Черновик не найден'}, status=404)
    
    try:
        item = AirplaneRequestItem.objects.get(request=draft, product_id=product_id)
    except AirplaneRequestItem.DoesNotExist:
        return Response({'error': 'Позиция не найдена'}, status=404)
    
    if quantity is not None:
        try:
            item.quantity = int(quantity)
            if item.quantity < 1:
                item.quantity = 1
        except ValueError:
            return Response({'error': 'Неверное значение quantity'}, status=400)
    
    if order is not None:
        try:
            item.order = int(order)
        except ValueError:
            return Response({'error': 'Неверное значение order'}, status=400)
    
    item.save()
    
    return Response({
        'id': item.id,
        'product_id': item.product.id,
        'quantity': item.quantity,
        'order': item.order,
        'result_field': item.result_field
    })


@api_view(['DELETE'])
def request_item_delete(request):
    """DELETE удаление услуги из заявки (без PK м-м)"""
    product_id = request.data.get('product_id')
    
    if not product_id:
        return Response({'error': 'Не указан product_id'}, status=400)
    
    user = get_current_user()
    draft = AirplaneRequest.objects.filter(creator=user, status='draft').first()
    
    if not draft:
        return Response({'error': 'Черновик не найден'}, status=404)
    
    try:
        item = AirplaneRequestItem.objects.get(request=draft, product_id=product_id)
    except AirplaneRequestItem.DoesNotExist:
        return Response({'error': 'Позиция не найдена'}, status=404)
    
    item.delete()
    
    return Response({'message': 'Позиция удалена', 'product_id': product_id})


# ==================== ДОМЕН: ПОЛЬЗОВАТЕЛИ ====================

@api_view(['POST'])
def user_register(request):
    """POST регистрация пользователя"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def user_login(request):
    """POST аутентификация (заглушка для 4 лабы)"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            'token': 'fake-jwt-token-for-lab4',
            'username': serializer.validated_data['username'],
            'message': 'Аутентификация (заглушка)'
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def user_logout(request):
    """POST деавторизация (заглушка для 4 лабы)"""
    return Response({'message': 'Деавторизация (заглушка)'})