from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import Service, Order, OrderService


def airplane_list(request):
    """Главная страница каталога с поиском через ORM"""
    search_query = request.GET.get('search_product', '').strip()
    
    # ORM-запрос: получаем только активные услуги
    services = Service.objects.filter(status='active')
    
    # Поиск по названию (регистронезависимый)
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    # Добавляем URL для изображений (как в старом коде)
    for service in services:
        if service.image_url:
            service.image_url_full = f"{settings.STATIC_URL}{service.image_url}"
        if service.video_url:
            service.video_url_full = f"{settings.MEDIA_URL}{service.video_url}"
    
    # Количество товаров в текущей корзине (черновике)
    cart_items_count = 0
    if request.user.is_authenticated:
        draft_order = Order.objects.filter(creator=request.user, status='draft').first()
        if draft_order:
            cart_items_count = OrderService.objects.filter(order=draft_order).count()
    
    context = {
        'products': services,
        'search_query': search_query,
        'cart_quantity': cart_items_count,
    }
    
    return render(request, 'airplane_list.html', context)


def aircraft_part_detail(request, part_id):
    """Детальная информация об услуге"""
    service = get_object_or_404(Service, id=part_id)
    
    # URL для видео (из бакета django-media)
    if service.video_url:
        service.video_url_full = f"{settings.MEDIA_URL}{service.video_url}"
    
    # URL для изображения
    if service.image_url:
        service.image_url_full = f"{settings.STATIC_URL}{service.image_url}"
    
    return render(request, 'airplane_product.html', {'product': service})


@login_required
def order_request(request):
    """Страница текущей заявки (корзины)"""
    # Получаем или создаём черновик
    draft_order, created = Order.objects.get_or_create(
        creator=request.user,
        status='draft',
        defaults={'status': 'draft'}
    )
    
    # Получаем услуги в заявке через m2m
    order_services = OrderService.objects.filter(order=draft_order).select_related('service')
    
    # Формируем список товаров для шаблона (как в старом коде)
    cart_items = []
    for item in order_services:
        service = item.service
        cart_items.append({
            'id': service.id,
            'title': service.name,
            'price': str(service.price),
            'price_display': f"{service.price:,.0f} ₽".replace(',', ' '),
            'quantity': item.quantity,
            'image': service.image_url,
            'image_url': f"{settings.STATIC_URL}{service.image_url}" if service.image_url else '',
        })
    
    # Рассчитываем общую сумму
    total_sum = sum(item.service.price * item.quantity for item in order_services)
    formatted_total_sum = f"{total_sum:,.0f}".replace(',', ' ')
    
    context = {
        'cart_items': cart_items,
        'total_sum': formatted_total_sum,
        'cart_items_count': len(cart_items),
    }
    
    return render(request, 'airplane_request.html', context)


@login_required
def add_to_cart(request, service_id):
    """Добавление услуги в заявку (через ORM) - POST метод"""
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id)
        
        # Получаем или создаём черновик
        draft_order, _ = Order.objects.get_or_create(
            creator=request.user,
            status='draft'
        )
        
        # Добавляем услугу в заявку (через ORM)
        order_service, created = OrderService.objects.get_or_create(
            order=draft_order,
            service=service,
            defaults={'quantity': 1}
        )
        if not created:
            order_service.quantity += 1
            order_service.save()
        
        return redirect('order_request')
    
    return redirect('airplane_list')


@login_required
def delete_current_order(request):
    """Логическое удаление заявки через сырой SQL UPDATE"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET status = 'deleted' "
                "WHERE creator_id = %s AND status = 'draft'",
                [request.user.id]
            )
    return redirect('airplane_list')