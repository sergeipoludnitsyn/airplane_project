from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.conf import settings
from .models import Service, Order, OrderService
from django.db.models import Sum, F, Q

def get_common_context(request):
    """Общий контекст для всех страниц"""
    # Получаем или создаём заявку-черновик (одна на всю сессию)
    order = Order.objects.filter(status='draft').first()
    cart_quantity = 0
    
    if order:
        cart_quantity = OrderService.objects.filter(
            order=order
        ).aggregate(total=Sum('quantity'))['total'] or 0
    
    return {
        'draft_order': order,
        'is_cart_active': order is not None,
        'cart_quantity': cart_quantity
    }

# СТРАНИЦА 1: Каталог услуг (GET + поиск)
def service_list(request):
    search_query = request.GET.get('search_product', '')
    
    if search_query:
        services = Service.objects.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query),
            status='active'
        )
    else:
        services = Service.objects.filter(status='active')
    
    products = []
    for service in services:
        products.append({
            'id': service.id,
            'title': service.name,
            'description': service.description,
            'price': f"{service.price} ₽",
            'image_url': service.image_url,
            'weight': service.weight,
            'material': service.material,
        })
    
    context = get_common_context(request)
    context.update({
        'products': products,
        'search_query': search_query
    })
    
    return render(request, 'airplane_list.html', context)

# Добавление в заявку (POST через ORM)
def add_to_order(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id, status='active')
        
        # Получаем или создаём единственную заявку-черновик
        order, created = Order.objects.get_or_create(
            status='draft',
            defaults={
                'status': 'draft',
                'client_name': 'Аэрофлот'
            }
        )
        
        # Добавляем услугу через ORM
        order_service, created = OrderService.objects.get_or_create(
            order=order,
            service=service,
            defaults={'quantity': 1}
        )
        
        if not created and order_service:
            order_service.quantity += 1
            order_service.save()
        
        return redirect('/')
    
    return redirect('/')

# СТРАНИЦА 2: Просмотр заявки (GET через ORM)
def order_request(request, order_id=None):
    # Если передан конкретный ID заявки
    if order_id is not None:
        order = get_object_or_404(Order, id=order_id)
        # Проверяем, не удалена ли заявка - редирект на главную
        if order.status == 'deleted':
            return redirect('/')
    else:
        # Если ID не указан, берем черновик
        order = Order.objects.filter(status='draft').first()
    
    # Если нет активной заявки - показываем пустую корзину
    if not order:
        context = get_common_context(request)
        context.update({
            'cart_items': [],
            'total_sum': 0,
            'organization': 'Аэрофлот',
            'order': None
        })
        return render(request, 'airplane_request.html', context)
    
    # Получаем услуги в заявке через ORM с join
    order_services = OrderService.objects.filter(order=order).select_related('service')
    
    cart_items = []
    total_sum = 0
    
    for item in order_services:
        # РАСЧЁТ СТОИМОСТИ: количество * цена услуги
        item_total = item.quantity * float(item.service.price)
        total_sum += item_total
        cart_items.append({
            'id': item.service.id,
            'title': item.service.name,
            'price': f"{item.service.price} ₽",
            'price_raw': float(item.service.price),
            'quantity': item.quantity,
            'image_url': item.service.image_url
        })
    
    context = get_common_context(request)
    context.update({
        'cart_items': cart_items,
        'total_sum': total_sum,
        'organization': order.client_name,
        'order': order
    })
    
    return render(request, 'airplane_request.html', context)

# Удаление заявки (POST через SQL UPDATE)
def delete_order_sql(request, order_id):
    if request.method == 'POST':
        # Сырой SQL UPDATE - требование задания
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET status = 'deleted' WHERE id = %s AND status = 'draft'",
                [order_id]
            )
    return redirect('/')

# СТРАНИЦА 3: Детальная страница услуги (с поддержкой видео)
def product_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id, status='active')
    
    context = get_common_context(request)
    
    # Формируем URL для видео (если есть)
    video_url = None
    poster_url = None
    
    if service.video_url:
        video_url = service.video_url
        # Если видео URL не полный, добавляем MEDIA_URL
        if not service.video_url.startswith('http'):
            video_url = f"{settings.MEDIA_URL}{service.video_url}"
    
    # Для постера используем image_url
    if service.image_url:
        poster_url = service.image_url
    
    context.update({
        'product': {
            'id': service.id,
            'title': service.name,
            'description': service.description,
            'price': f"{service.price} ₽",
            'image_url': service.image_url,
            'video_url': video_url,
            'poster_url': poster_url,
            'width': '-',
            'height': '-',
            'depth': '-',
            'material': service.material,
            'manufacturer': service.manufacturer,
            'waist_cushion': '-',
            'fold_table': '-',
        }
    })
    
    return render(request, 'airplane_product.html', context)