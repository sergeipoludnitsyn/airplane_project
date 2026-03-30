# views.py

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.conf import settings

# Общий список продуктов
PRODUCTS = [
    {
        'id': 1, 
        'title': 'Кресло эконом класса', 
        'price': '920 000 ₽', 
        'image': 'images/chair_econom.jpg',      # В django-static/images/
        'video': 'chair_econom.mp4',      # В django-media/videos/
        'poster': 'images/chair_econom_poster.jpg',  # В django-static/images/
        'description': 'Удобное кресло для пассажиров эконом-класса.', 
        'width': '620', 
        'height': '1180', 
        'depth': '360', 
        'material': 'ткань', 
        'waist_cushion': 'нет', 
        'fold_table': 'да'
    },
    {
        'id': 2, 
        'title': 'Персональный телевизор (PTV)', 
        'price': '62 550 ₽', 
        'image': 'images/PTV.jpg',
        'video': 'PTV.mp4',
        'poster': 'images/PTV_poster.jpg',
        'description': 'Современный персональный телевизор для развлечений.', 
        'width': '-', 
        'height': '-', 
        'depth': '-', 
        'material': '-', 
        'waist_cushion': '-', 
        'fold_table': '-'
    },
    {
        'id': 3, 
        'title': 'Потолочный телевизор', 
        'price': '52 110 ₽', 
        'image': 'images/PTV_2.jpg',
        'video': 'PTV_2.mp4',
        'poster': 'images/PTV_2_poster.jpg',
        'description': 'Высококачественный потолочный телевизор.', 
        'width': '-', 
        'height': '-', 
        'depth': '-', 
        'material': '-', 
        'waist_cushion': '-', 
        'fold_table': '-'
    },
    {
        'id': 4, 
        'title': 'Кресло бизнес класса', 
        'price': '352 180 ₽', 
        'image': 'images/chair_business_1.jpg',
        'video': 'chair_business_1.mp4',
        'poster': 'images/chair_business_1_poster.jpg',
        'description': 'Премиальное кресло для комфорта пассажиров.', 
        'width': '-', 
        'height': '-', 
        'depth': '-', 
        'material': '-', 
        'waist_cushion': '-', 
        'fold_table': '-'
    },
    {
        'id': 5, 
        'title': 'Кресло бизнес класса (люкс)', 
        'price': '920 000 ₽', 
        'image': 'images/chair_business_2.jpg',
        'video': 'chair_business_2.mp4',
        'poster': 'images/chair_business_2_poster.jpg',
        'description': 'Премиальное кресло для максимального комфорта.', 
        'width': '-', 
        'height': '-', 
        'depth': '-', 
        'material': '-', 
        'waist_cushion': '-', 
        'fold_table': '-'
    },
]

def catalog(request):
    """Главная страница каталога — изображения из django-static/images/"""
    for product in PRODUCTS:
        product['image_url'] = f"{settings.STATIC_URL}{product['image']}"
    
    return render(request, 'catalog.html', {'products': PRODUCTS})

def product_detail(request, product_id):
    """Подробная информация о товаре — видео из django-media/"""
    product = next((item for item in PRODUCTS if item['id'] == int(product_id)), None)
    if product is None:
        raise Http404("Продукт не найден")
    
    # URL для видео (из бакета django-media)
    if product.get('video'):
        product['video_url'] = f"{settings.MEDIA_URL}{product['video']}"
        print(f"Video URL: {product['video_url']}")  # Отладка
    
    # URL для постера (из бакета django-static)
    if product.get('poster'):
        product['poster_url'] = f"{settings.STATIC_URL}{product['poster']}"
    
    # URL для изображения (как запасной вариант)
    if product.get('image'):
        product['image_url'] = f"{settings.STATIC_URL}{product['image']}"
    
    return render(request, 'product_detail.html', {'product': product})

def order_application(request):
    """Страница оформления заявки — изображения из django-static/images/"""
    cart_items = [
        {
            'title': 'Кресло эконом класса', 
            'price': '920 000', 
            'quantity': 197,
            'image': 'images/chair_econom.jpg'
        },
        {
            'title': 'Персональный телевизор (PTV)', 
            'price': '62 550', 
            'quantity': 197,
            'image': 'images/PTV.jpg'
        },
        {
            'title': 'Кресло бизнес класса', 
            'price': '352 180', 
            'quantity': 18,
            'image': 'images/chair_business_1.jpg'
        },
    ]
    
    for item in cart_items:
        item['image_url'] = f"{settings.STATIC_URL}{item['image']}"
    
    total_sum = 0
    for item in cart_items:
        price_str = str(item['price']).replace(' ', '').replace('₽', '')
        price = int(price_str)
        total_sum += price * item['quantity']
    
    formatted_total_sum = f"{total_sum:,}".replace(',', ' ') + " ₽"
    
    context = {
        'cart_items': cart_items,
        'total_sum': formatted_total_sum,
    }
    

    
    return render(request, 'application.html', context)