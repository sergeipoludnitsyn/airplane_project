from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from .models import AirplaneProduct, AirplaneRequest, AirplaneRequestItem
from django.db.models import Sum, Q

def get_common_context(request):
    order = AirplaneRequest.objects.filter(status='draft').first()
    cart_quantity = 0
    if order:
        cart_quantity = AirplaneRequestItem.objects.filter(request=order).aggregate(total=Sum('quantity'))['total'] or 0
    return {
        'draft_order': order,
        'is_cart_active': order is not None,
        'cart_quantity': cart_quantity
    }

def service_list(request):
    search_query = request.GET.get('search_product', '')
    if search_query:
        products = AirplaneProduct.objects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query),
            status='active'
        )
    else:
        products = AirplaneProduct.objects.filter(status='active')
    
    products_list = []
    for p in products:
        products_list.append({
            'id': p.id,
            'title': p.name,
            'description': p.description,
            'price': f"{p.price} ₽",
            'image_url': p.image_url,
            'weight': p.weight,
            'material': p.material,
        })
    
    context = get_common_context(request)
    context.update({'products': products_list, 'search_query': search_query})
    return render(request, 'airplane_list.html', context)

def add_to_order(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(AirplaneProduct, id=product_id, status='active')
        order, created = AirplaneRequest.objects.get_or_create(
            status='draft',
            defaults={'status': 'draft', 'client_name': 'Аэрофлот'}
        )
        item, created = AirplaneRequestItem.objects.get_or_create(
            request=order, product=product, defaults={'quantity': 1}
        )
        if not created:
            item.quantity += 1
            item.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    return redirect('/')

def order_request(request, order_id=None):
    order = AirplaneRequest.objects.filter(status='draft').first()
    if not order:
        context = get_common_context(request)
        context.update({'cart_items': [], 'total_sum': 0, 'organization': 'Аэрофлот', 'order': None})
        return render(request, 'airplane_request.html', context)
    
    items = AirplaneRequestItem.objects.filter(request=order).select_related('product')
    cart_items = []
    total_sum = 0
    for item in items:
        item_total = item.quantity * float(item.product.price)
        total_sum += item_total
        cart_items.append({
            'id': item.product.id,
            'title': item.product.name,
            'price': f"{item.product.price} ₽",
            'price_raw': float(item.product.price),
            'quantity': item.quantity,
            'image_url': item.product.image_url
        })
    context = get_common_context(request)
    context.update({'cart_items': cart_items, 'total_sum': total_sum, 'organization': order.client_name, 'order': order})
    return render(request, 'airplane_request.html', context)

def delete_order_sql(request, order_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("UPDATE airplane_requests SET status = 'deleted' WHERE id = %s AND status = 'draft'", [order_id])
    return redirect('/')

def product_detail(request, product_id):
    product = get_object_or_404(AirplaneProduct, id=product_id, status='active')
    context = get_common_context(request)
    context['product'] = {
        'id': product.id,
        'title': product.name,
        'description': product.description,
        'price': f"{product.price} ₽",
        'image_url': product.image_url,
        'video_url': product.video_url,
        'width': '-',
        'height': '-',
        'depth': '-',
        'material': product.material,
        'manufacturer': product.manufacturer,
        'waist_cushion': '-',
        'fold_table': '-',
    }
    return render(request, 'airplane_product.html', context)