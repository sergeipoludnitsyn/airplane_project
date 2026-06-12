from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from .models import Airplane, Configuration, AirplaneConfiguration
from django.db.models import Sum, Q

def get_common_context(request):
    """Общий контекст для всех HTML страниц"""
    config = Configuration.objects.filter(status='draft').first()
    cart_quantity = 0
    if config:
        cart_quantity = AirplaneConfiguration.objects.filter(configuration=config).aggregate(total=Sum('quantity'))['total'] or 0
    return {
        'draft_config': config,
        'is_cart_active': config is not None,
        'cart_quantity': cart_quantity
    }

def airplane_list_html(request):
    """Главная страница: список самолётов"""
    search_query = request.GET.get('search_product', '')
    
    if search_query:
        airplanes = Airplane.objects.filter(
            Q(model_name__icontains=search_query) | Q(description__icontains=search_query),
            status='active'
        )
    else:
        airplanes = Airplane.objects.filter(status='active')
    
    airplanes_list = []
    for a in airplanes:
        airplanes_list.append({
            'id': a.id,
            'title': a.model_name,
            'description': a.description,
            'price': f"{a.price} ₽",
            'image_url': a.image_url,
            'weight': a.weight,
            'manufacturer': a.manufacturer,
        })
    
    context = get_common_context(request)
    context.update({'products': airplanes_list, 'search_query': search_query})
    return render(request, 'airplane_list.html', context)

def add_to_configuration(request, airplane_id):
    """Добавление самолёта в конфигурацию (HTML форма)"""
    if request.method == 'POST':
        airplane = get_object_or_404(Airplane, id=airplane_id, status='active')
        config, created = Configuration.objects.get_or_create(
            status='draft',
            defaults={'status': 'draft', 'customer_name': 'Аэрофлот'}
        )
        item, created = AirplaneConfiguration.objects.get_or_create(
            configuration=config, airplane=airplane, defaults={'quantity': 1}
        )
        if not created:
            item.quantity += 1
            item.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')

def configuration_html(request, config_id=None):
    """Страница конфигурации (корзина/заявка)"""
    config = Configuration.objects.filter(status='draft').first()
    if not config:
        context = get_common_context(request)
        context.update({'cart_items': [], 'total_sum': 0, 'organization': 'Аэрофлот', 'configuration': None})
        return render(request, 'configuration.html', context)
    
    items = AirplaneConfiguration.objects.filter(configuration=config).select_related('airplane')
    cart_items = []
    total_sum = 0
    for item in items:
        item_total = item.quantity * float(item.airplane.price)
        total_sum += item_total
        cart_items.append({
            'id': item.airplane.id,
            'title': item.airplane.model_name,
            'price': f"{item.airplane.price} ₽",
            'price_raw': float(item.airplane.price),
            'quantity': item.quantity,
            'image_url': item.airplane.image_url
        })
    
    context = get_common_context(request)
    context.update({
        'cart_items': cart_items,
        'total_sum': total_sum,
        'organization': config.customer_name,
        'configuration': config
    })
    return render(request, 'configuration.html', context)

def delete_configuration_sql(request, config_id):
    """Удаление конфигурации через SQL UPDATE"""
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE configurations SET status = 'deleted' WHERE id = %s AND status = 'draft'",
                [config_id]
            )
    return redirect('/')

def airplane_detail_html(request, airplane_id):
    """Страница деталей самолёта"""
    airplane = get_object_or_404(Airplane, id=airplane_id, status='active')
    context = get_common_context(request)
    context['product'] = {
        'id': airplane.id,
        'title': airplane.model_name,
        'description': airplane.description,
        'price': f"{airplane.price} ₽",
        'image_url': airplane.image_url,
        'video_url': airplane.video_url,
        'width': getattr(airplane, 'width', '-'),
        'height': getattr(airplane, 'height', '-'),
        'depth': getattr(airplane, 'depth', '-'),
        'material': getattr(airplane, 'material', '-'),
        'manufacturer': airplane.manufacturer,
        'max_speed': airplane.max_speed,
        'range_km': airplane.range_km,
        'weight': airplane.weight,
    }
    return render(request, 'airplane_detail.html', context)