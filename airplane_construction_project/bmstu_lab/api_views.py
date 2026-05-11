from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from .models import Service, Order, OrderService
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer,
    OrderServiceSerializer, OrderListSerializer, OrderDetailSerializer,
    OrderUpdateSerializer, OrderFormSerializer, OrderModerateSerializer,
    CartIconSerializer, UserRegisterSerializer
)
from .utils import get_current_creator

# ========== ДОМЕН УСЛУГ ==========

@api_view(['GET'])
def service_list(request):
    """GET список услуг с фильтрацией"""
    queryset = Service.objects.filter(status='active')
    
    # Фильтрация по названию
    name = request.query_params.get('name', None)
    if name:
        queryset = queryset.filter(name__icontains=name)
    
    # Фильтрация по цене
    price_min = request.query_params.get('price_min', None)
    price_max = request.query_params.get('price_max', None)
    if price_min:
        queryset = queryset.filter(price__gte=price_min)
    if price_max:
        queryset = queryset.filter(price__lte=price_max)
    
    serializer = ServiceSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def service_detail(request, pk):
    """GET одна запись услуги"""
    try:
        service = Service.objects.get(pk=pk, status='active')
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ServiceSerializer(service)
    return Response(serializer.data)


@api_view(['POST'])
def service_create(request):
    """POST добавление услуги + добавление файлов в MinIO"""
    serializer = ServiceCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Генерация имён файлов на латинице
    image_filename = None
    video_filename = None
    
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        ext = image_file.name.split('.')[-1]
        image_filename = f"services/{uuid.uuid4().hex}.{ext}"
        default_storage.save(image_filename, ContentFile(image_file.read()))
    
    if 'video' in request.FILES:
        video_file = request.FILES['video']
        ext = video_file.name.split('.')[-1]
        video_filename = f"services/{uuid.uuid4().hex}.{ext}"
        default_storage.save(video_filename, ContentFile(video_file.read()))
    
    service = Service.objects.create(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        width=data.get('width', ''),
        height=data.get('height', ''),
        depth=data.get('depth', ''),
        material=data.get('material', ''),
        image_url=image_filename,
        video_url=video_filename,
        status='active'
    )
    
    return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)


# ========== ДОМЕН М-М ==========

@api_view(['DELETE'])
def order_service_delete(request, order_id, service_id):
    """DELETE удаление из заявки (без PK м-м)"""
    creator = get_current_creator()
    
    try:
        order = Order.objects.get(id=order_id, creator=creator, status='draft')
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in draft'}, status=status.HTTP_404_NOT_FOUND)
    
    deleted, _ = OrderService.objects.filter(order=order, service_id=service_id).delete()
    
    if deleted:
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response({'error': 'Service not found in order'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def order_service_update(request, order_id, service_id):
    """PUT изменение количества в м-м (без PK м-м)"""
    creator = get_current_creator()
    
    try:
        order = Order.objects.get(id=order_id, creator=creator, status='draft')
        order_service = OrderService.objects.get(order=order, service_id=service_id)
    except (Order.DoesNotExist, OrderService.DoesNotExist):
        return Response({'error': 'Order or service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    quantity = request.data.get('quantity')
    if quantity is None or int(quantity) < 1:
        return Response({'error': 'Quantity must be >= 1'}, status=status.HTTP_400_BAD_REQUEST)
    
    order_service.quantity = int(quantity)
    order_service.save()
    
    serializer = OrderServiceSerializer(order_service)
    return Response(serializer.data)


@api_view(['POST'])
def order_service_add(request, service_id):
    """POST добавления в заявку-черновик"""
    creator = get_current_creator()
    
    # Получаем или создаём черновик
    order, _ = Order.objects.get_or_create(
        creator=creator,
        status='draft',
        defaults={'status': 'draft'}
    )
    
    try:
        service = Service.objects.get(id=service_id, status='active')
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    order_service, created = OrderService.objects.get_or_create(
        order=order,
        service=service,
        defaults={'quantity': 1}
    )
    
    if not created:
        order_service.quantity += 1
        order_service.save()
    
    serializer = OrderServiceSerializer(order_service)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ========== ДОМЕН ЗАЯВКИ ==========

@api_view(['GET'])
def cart_icon(request):
    """GET иконки корзины (id черновика и количество услуг)"""
    creator = get_current_creator()
    
    try:
        order = Order.objects.get(creator=creator, status='draft')
        items_count = order.orderservice_set.count()
    except Order.DoesNotExist:
        order = None
        items_count = 0
    
    data = {
        'order_id': order.id if order else None,
        'items_count': items_count
    }
    serializer = CartIconSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
def order_list(request):
    """GET список (кроме удаленных и черновика) с фильтрацией"""
    creator = get_current_creator()
    
    # Исключаем удаленные и черновики
    queryset = Order.objects.exclude(status__in=['deleted', 'draft'])
    
    # Фильтрация по диапазону даты формирования
    formed_after = request.query_params.get('formed_after', None)
    formed_before = request.query_params.get('formed_before', None)
    
    if formed_after:
        queryset = queryset.filter(formed_at__gte=formed_after)
    if formed_before:
        queryset = queryset.filter(formed_at__lte=formed_before)
    
    # Фильтрация по статусу
    status_filter = request.query_params.get('status', None)
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    serializer = OrderListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def order_detail(request, pk):
    """GET одна запись (поля заявки + её услуги)"""
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderDetailSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
def order_update(request, pk):
    """PUT изменения полей заявки по теме"""
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Обновляем поля по теме (добавьте свои поля)
    # order.some_field = serializer.validated_data.get('some_field', order.some_field)
    order.save()
    
    return Response(OrderDetailSerializer(order).data)


@api_view(['PUT'])
def order_form(request, pk):
    """PUT сформировать создателем (дата формирования)"""
    creator = get_current_creator()
    
    try:
        order = Order.objects.get(pk=pk, creator=creator, status='draft')
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in draft'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderFormSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Проверка обязательных полей (по вашей теме)
    # if not order.some_required_field:
    #     return Response({'error': 'Required fields missing'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Расчёт стоимости заказа (формула из лаб-2)
    total_price = 0
    for os in order.orderservice_set.all():
        total_price += float(os.service.price) * os.quantity
    
    # Добавляем наценку за количество уникальных деталей
    unique_parts = order.orderservice_set.count()
    total_price = total_price * (1 + unique_parts * 0.05)
    
    order.total_price = total_price
    order.status = 'formed'
    order.formed_at = timezone.now()
    order.save()
    
    return Response(OrderDetailSerializer(order).data)


@api_view(['PUT'])
def order_moderate(request, pk):
    """PUT завершить/отклонить модератором"""
    try:
        order = Order.objects.get(pk=pk, status='formed')
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in formed status'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderModerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    action = serializer.validated_data['action']
    
    if action == 'complete':
        order.status = 'completed'
    elif action == 'reject':
        order.status = 'rejected'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    order.completed_at = timezone.now()
    order.save()
    
    return Response(OrderDetailSerializer(order).data)


@api_view(['DELETE'])
def order_delete(request, pk):
    """DELETE удаление (дата формирования)"""
    creator = get_current_creator()
    
    try:
        order = Order.objects.get(pk=pk, creator=creator)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    
    order.status = 'deleted'
    order.save()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


# ========== ДОМЕН ПОЛЬЗОВАТЕЛЬ ==========

@api_view(['POST'])
def user_register(request):
    """POST регистрация"""
    serializer = UserRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.save()
    return Response({'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def user_login(request):
    """POST аутентификация (заглушка)"""
    # Заглушка для 4-й лабораторной
    return Response({'message': 'Login endpoint (placeholder)'})


@api_view(['POST'])
def user_logout(request):
    """POST деавторизация (заглушка)"""
    # Заглушка для 4-й лабораторной
    return Response({'message': 'Logout endpoint (placeholder)'})