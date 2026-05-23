from rest_framework import serializers
from .models import AirplaneProduct, AirplaneRequest, AirplaneRequestItem
from django.contrib.auth.models import User


class AirplaneProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneProduct
        fields = '__all__'
        read_only_fields = ['id', 'status']


class AirplaneProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneProduct
        fields = ['name', 'description', 'price', 'weight', 'material', 'manufacturer', 'image_url', 'video_url']
        read_only_fields = ['id', 'status']


class AirplaneRequestItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)
    product_image = serializers.URLField(source='product.image_url', read_only=True)
    
    class Meta:
        model = AirplaneRequestItem
        fields = ['id', 'request', 'product', 'product_name', 'product_price', 
                  'product_image', 'quantity', 'order', 'result_field']
        read_only_fields = ['id', 'request']


class AirplaneRequestListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    moderator_name = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    result_items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AirplaneRequest
        fields = ['id', 'status', 'created_at', 'formed_at', 'completed_at', 
                  'client_name', 'purpose', 'aircraft_model', 
                  'creator_name', 'moderator_name', 'result_items_count']
    
    def get_result_items_count(self, obj):
        """Количество позиций с непустым result_field"""
        return obj.items.filter(result_field__isnull=False).count()


class AirplaneRequestDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    moderator_name = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    items = AirplaneRequestItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = AirplaneRequest
        fields = '__all__'


class AirplaneRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneRequest
        fields = ['client_name', 'purpose', 'aircraft_model', 'special_request']


class AirplaneRequestFormSerializer(serializers.Serializer):
    """Сериализатор для формирования заявки (пустой, т.к. данные из PUT)"""
    pass


class AirplaneRequestModerateSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['complete', 'reject'])


class CartIconSerializer(serializers.Serializer):
    request_id = serializers.IntegerField(allow_null=True)
    items_count = serializers.IntegerField()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)


class UserLogoutSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)