# views.py

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.conf import settings

# Общий список продуктов (комплектующих для самолёта)
AIRCRAFT_PARTS = [
    {
        'id': 1, 
        'title': 'Кресло эконом класса', 
        'price': '920 000 ₽', 
        'image': 'images/chair_econom.jpg',
        'video': 'chair_econom.mp4',
        'poster': 'images/chair_econom_poster.jpg',
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

# Данные корзины (только ID товаров и количество)
CART_ITEMS = [
    {'product_id': 1, 'quantity': 197},  # Кресло эконом класса
    {'product_id': 2, 'quantity': 197},  # Персональный телевизор (PTV)
    {'product_id': 4, 'quantity': 18},   # Кресло бизнес класса
]

def get_part_by_id(part_id):
    """Получить комплектующую по ID"""
    return next((part for part in AIRCRAFT_PARTS if part['id'] == part_id), None)

def get_cart_items_with_details():
    """Получить полную информацию о товарах в корзине на основе ID"""
    cart_with_details = []
    
    for cart_item in CART_ITEMS:
        part = get_part_by_id(cart_item['product_id'])
        if part:
            # Извлекаем числовое значение цены (убираем пробелы и ₽)
            price_value = part['price'].replace(' ', '').replace('₽', '')
            
            cart_with_details.append({
                'id': part['id'],
                'title': part['title'],
                'price': price_value,
                'price_display': part['price'],
                'quantity': cart_item['quantity'],
                'image': part['image'],
                'image_url': f"{settings.STATIC_URL}{part['image']}",
            })
    
    return cart_with_details

def get_cart_unique_items_count():
    """Возвращает количество уникальных товаров (позиций) в корзине"""
    return len(CART_ITEMS)

def get_cart_total_quantity():
    """Возвращает общее количество единиц товаров в корзине"""
    return sum(item['quantity'] for item in CART_ITEMS)

def airplane_list(request):
    """Главная страница каталога комплектующих для самолёта с возможностью поиска"""
    
    # Получаем поисковый запрос из GET параметров
    search_query = request.GET.get('search_product', '').strip()
    
    # Создаем копию списка продуктов для фильтрации
    filtered_parts = AIRCRAFT_PARTS.copy()
    
    # Если есть поисковый запрос, фильтруем товары
    if search_query:
        filtered_parts = [
            part for part in AIRCRAFT_PARTS 
            if search_query.lower() in part['title'].lower()
        ]
    
    # Добавляем URL для изображений
    for part in filtered_parts:
        part['image_url'] = f"{settings.STATIC_URL}{part['image']}"
    
    # Получаем количество уникальных товаров в корзине
    cart_items_count = get_cart_unique_items_count()
    
    context = {
        'products': filtered_parts,
        'search_query': search_query,
        'cart_quantity': cart_items_count,
    }
    
    return render(request, 'airplane_list.html', context)

def aircraft_part_detail(request, part_id):
    """Детальная информация о комплектующей для самолёта — видео из django-media/"""
    part = get_part_by_id(int(part_id))
    if part is None:
        raise Http404("Комплектующая не найдена")
    
    # URL для видео (из бакета django-media)
    if part.get('video'):
        part['video_url'] = f"{settings.MEDIA_URL}{part['video']}"
        print(f"Video URL: {part['video_url']}")  # Отладка
    
    # URL для постера (из бакета django-static)
    if part.get('poster'):
        part['poster_url'] = f"{settings.STATIC_URL}{part['poster']}"
    
    # URL для изображения (как запасной вариант)
    if part.get('image'):
        part['image_url'] = f"{settings.STATIC_URL}{part['image']}"
    
    return render(request, 'airplane_product.html', {'product': part})

def order_request(request):
    """Страница оформления заявки на комплектующие для самолёта"""
    
    # Получаем полную информацию о товарах в корзине
    cart_items = get_cart_items_with_details()
    
    # Вычисляем общую сумму
    total_sum = 199901590

    formatted_total_sum = f"{total_sum:,}".replace(',', ' ')
    
    context = {
        'cart_items': cart_items,
        'total_sum': formatted_total_sum,
        'cart_items_count': len(cart_items),
    }
    
    # ИЗМЕНЕНО: airplane_request.html
    return render(request, 'airplane_request.html', context)