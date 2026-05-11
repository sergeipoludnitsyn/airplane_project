from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Service, Order, OrderService
from .utils import get_current_creator

# ========== СЕРИАЛИЗАТОРЫ ДЛЯ УСЛУГ ==========
class ServiceSerializer(serializers.ModelSerializer):
    image_url_full = serializers.SerializerMethodField()
    video_url_full = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'width', 'height', 
                  'depth', 'material', 'image_url', 'video_url', 'status',
                  'image_url_full', 'video_url_full']
        read_only_fields = ['id', 'status']
    
    def get_image_url_full(self, obj):
        if obj.image_url:
            return f"http://localhost:9000/django-static/{obj.image_url}"
        return None
    
    def get_video_url_full(self, obj):
        if obj.video_url:
            return f"http://localhost:9000/django-media/{obj.video_url}"
        return None


class ServiceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    width = serializers.CharField(max_length=50, required=False, allow_blank=True)
    height = serializers.CharField(max_length=50, required=False, allow_blank=True)
    depth = serializers.CharField(max_length=50, required=False, allow_blank=True)
    material = serializers.CharField(max_length=100, required=False, allow_blank=True)
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)


# ========== СЕРИАЛИЗАТОРЫ ДЛЯ М-М ==========
class OrderServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=12, decimal_places=2, read_only=True)
    service_image = serializers.CharField(source='service.image_url', read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderService
        fields = ['id', 'order', 'service', 'service_name', 'service_price', 
                  'service_image', 'quantity', 'total']
        read_only_fields = ['id', 'order']
    
    def get_total(self, obj):
        return float(obj.service.price) * obj.quantity


# ========== СЕРИАЛИЗАТОРЫ ДЛЯ ЗАЯВОК ==========
class OrderListSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    services_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'formed_at', 'completed_at',
                  'creator_username', 'moderator_username', 'total_price',
                  'services_count']
    
    def get_services_count(self, obj):
        return obj.orderservice_set.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    moderator_username = serializers.CharField(source='moderator.username', read_only=True)
    services = OrderServiceSerializer(source='orderservice_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'formed_at', 'completed_at',
                  'creator_username', 'moderator_username', 'total_price',
                  'services']


class OrderUpdateSerializer(serializers.Serializer):
    """Для изменения полей заявки по теме"""
    # Добавьте поля по вашей теме (например, для самолётостроения)
    # Пока оставим пустым или добавим общее поле
    comment = serializers.CharField(required=False, allow_blank=True)


class OrderFormSerializer(serializers.Serializer):
    """Для формирования заявки создателем"""
    # Обязательные поля для формирования
    # Добавьте по вашей теме
    pass


class OrderModerateSerializer(serializers.Serializer):
    """Для модерации заявки (завершить/отклонить)"""
    action = serializers.ChoiceField(choices=['complete', 'reject'])


# ========== СЕРИАЛИЗАТОР ДЛЯ КОРЗИНЫ ==========
class CartIconSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    items_count = serializers.IntegerField()


# ========== СЕРИАЛИЗАТОРЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ==========
class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user