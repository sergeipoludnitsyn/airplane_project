from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import connection
from django.db.models import Sum, F
from django.conf import settings
from .models import Service, Order, OrderService
import json

def get_or_create_draft_order(request):
    """Получить или создать черновик заявки (без пользователя)"""
    # Используем сессию для идентификации корзины
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    # Создаём или получаем заявку по session_key
    order, created = Order.objects.get_or_create(
        session_key=session_key,
        status='draft',
        defaults={'status': 'draft'}
    )
    return order

def airplane_list(request):
    search_query = request.GET.get('search_product', '').strip()
    services = Service.objects.filter(status='active')
    
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    for service in services:
        if service.image_url:
            service.image_url_full = f"{settings.STATIC_URL}{service.image_url}"
        if service.video_url:
            service.video_url_full = f"{settings.MEDIA_URL}{service.video_url}"
    
    order = get_or_create_draft_order(request)
    cart_items_count = OrderService.objects.filter(order=order).count()
    
    context = {
        'products': services,
        'search_query': search_query,
        'cart_quantity': cart_items_count,
    }
    return render(request, 'airplane_list.html', context)

def aircraft_part_detail(request, part_id):
    service = get_object_or_404(Service, id=part_id, status='active')
    
    if service.image_url:
        service.image_url_full = f"{settings.STATIC_URL}{service.image_url}"
    if service.video_url:
        service.video_url_full = f"{settings.MEDIA_URL}{service.video_url}"
    
    return render(request, 'airplane_product.html', {'product': service})

def order_request(request):
    order = get_or_create_draft_order(request)
    order_services = OrderService.objects.filter(order=order).select_related('service')
    
    cart_items = []
    total_sum = 0
    
    for os in order_services:
        service = os.service
        item_total = float(service.price) * os.quantity
        total_sum += item_total
        
        cart_items.append({
            'id': service.id,
            'title': service.name,
            'price': str(service.price),
            'price_display': f"{float(service.price):,.0f} ₽".replace(',', ' '),
            'quantity': os.quantity,
            'image': service.image_url,
            'image_url': f"{settings.STATIC_URL}{service.image_url}" if service.image_url else '',
            'total': item_total,
        })
    
    order.total_price = total_sum
    order.save()
    
    context = {
        'cart_items': cart_items,
        'total_sum': f"{total_sum:,.0f}".replace(',', ' '),
        'cart_items_count': len(cart_items),
        'order_id': order.id,
    }
    return render(request, 'airplane_request.html', context)

def add_to_cart(request, service_id):
    if request.method == 'POST':
        service = get_object_or_404(Service, id=service_id, status='active')
        order = get_or_create_draft_order(request)
        
        order_service, created = OrderService.objects.get_or_create(
            order=order,
            service=service,
            defaults={'quantity': 1}
        )
        if not created:
            order_service.quantity += 1
            order_service.save()
        
        return redirect('airplane_list')
    return redirect('airplane_list')

def delete_current_order(request):
    """Логическое удаление заявки через SQL UPDATE"""
    if request.method == 'POST':
        order = get_or_create_draft_order(request)
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET status = 'deleted' WHERE id = %s AND status = 'draft'",
                [order.id]
            )
    return redirect('airplane_list')

def update_cart_quantity(request, service_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            change = int(data.get('change', 0))
            
            order = get_or_create_draft_order(request)
            order_service = OrderService.objects.get(order=order, service_id=service_id)
            new_quantity = order_service.quantity + change
            
            if new_quantity <= 0:
                order_service.delete()
                new_quantity = 0
            else:
                order_service.quantity = new_quantity
                order_service.save()
            
            total_sum = OrderService.objects.filter(order=order).aggregate(
                total=Sum(F('quantity') * F('service__price'))
            )['total'] or 0
            
            order.total_price = total_sum
            order.save()
            
            service = Service.objects.get(id=service_id)
            
            return JsonResponse({
                'success': True,
                'new_quantity': new_quantity,
                'price_per_unit': float(service.price),
                'total_sum': float(total_sum)
            })
        except OrderService.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден в заявке'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def order_detail(request, order_id):
    """Просмотр конкретной заявки по ID"""
    order = get_object_or_404(Order, id=order_id)
    
    order_services = OrderService.objects.filter(order=order).select_related('service')
    
    cart_items = []
    total_sum = 0
    
    for os in order_services:
        service = os.service
        item_total = float(service.price) * os.quantity
        total_sum += item_total
        
        cart_items.append({
            'id': service.id,
            'title': service.name,
            'price': str(service.price),
            'price_display': f"{float(service.price):,.0f} ₽".replace(',', ' '),
            'quantity': os.quantity,
            'image': service.image_url,
            'image_url': f"{settings.STATIC_URL}{service.image_url}" if service.image_url else '',  # ← ДОБАВИТЬ
            'total': item_total,
        })
    
    context = {
        'cart_items': cart_items,
        'total_sum': f"{total_sum:,.0f}".replace(',', ' '),
        'cart_items_count': len(cart_items),
        'order_id': order.id,
        'order_status': order.status,
    }
    return render(request, 'airplane_request.html', context)