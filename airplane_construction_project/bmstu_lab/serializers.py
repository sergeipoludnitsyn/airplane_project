from rest_framework import serializers
from .models import Airplane, Configuration, AirplaneConfiguration
from django.contrib.auth.models import User


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'
        read_only_fields = ['id', 'status']


class AirplaneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ['model_name', 'description', 'price', 'weight', 'max_speed', 
                  'range_km', 'manufacturer', 'image_url', 'video_url']


class AirplaneConfigurationSerializer(serializers.ModelSerializer):
    airplane_name = serializers.CharField(source='airplane.model_name', read_only=True)
    airplane_price = serializers.DecimalField(source='airplane.price', max_digits=12, decimal_places=2, read_only=True)
    airplane_image = serializers.URLField(source='airplane.image_url', read_only=True)
    
    class Meta:
        model = AirplaneConfiguration
        fields = ['id', 'configuration', 'airplane', 'airplane_name', 'airplane_price',
                  'airplane_image', 'quantity', 'order_index', 'result_field']
        read_only_fields = ['id', 'configuration']


class ConfigurationListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    moderator_name = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    items_count = serializers.SerializerMethodField()
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Configuration
        fields = ['id', 'status', 'created_at', 'formed_at', 'completed_at',
                  'customer_name', 'purpose', 'aircraft_model', 'mm_field',
                  'creator_name', 'moderator_name', 'items_count', 'total_cost']
    
    def get_items_count(self, obj):
        return obj.items.count()


class ConfigurationDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    moderator_name = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    items = AirplaneConfigurationSerializer(many=True, read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Configuration
        fields = '__all__'


class ConfigurationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['customer_name', 'purpose', 'aircraft_model', 'mm_field']


class ConfigurationModerateSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['complete', 'reject'])


# ========== Singleton демонстрация ==========
class SingletonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


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


# ==================== АУТЕНТИФИКАЦИЯ ====================

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'date_joined']


class CartIconSerializer(serializers.Serializer):
    configuration_id = serializers.IntegerField(allow_null=True)
    items_count = serializers.IntegerField()