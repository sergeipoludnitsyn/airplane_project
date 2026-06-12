from django.db import models
from django.contrib.auth.models import User

class Airplane(models.Model):
    """Самолёт (аналог Service)"""
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удалён'),
    ]
    
    model_name = models.CharField(max_length=200, verbose_name="Модель самолёта")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    image_url = models.URLField(null=True, blank=True, verbose_name="URL изображения")
    video_url = models.URLField(null=True, blank=True, verbose_name="URL видео")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Характеристики
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Вес (кг)")
    max_speed = models.IntegerField(null=True, blank=True, verbose_name="Макс. скорость (км/ч)")
    range_km = models.IntegerField(null=True, blank=True, verbose_name="Дальность полёта (км)")
    manufacturer = models.CharField(max_length=200, default="Боинг", verbose_name="Производитель")
    
    # Дополнительные характеристики
    width = models.IntegerField(null=True, blank=True, verbose_name="Ширина (мм)")
    height = models.IntegerField(null=True, blank=True, verbose_name="Высота (мм)")
    depth = models.IntegerField(null=True, blank=True, verbose_name="Глубина (мм)")
    material = models.CharField(max_length=200, null=True, blank=True, verbose_name="Материал")
    
    class Meta:
        db_table = 'airplanes'
        verbose_name = "Самолёт"
        verbose_name_plural = "Самолёты"
    
    def __str__(self):
        return self.model_name


class Configuration(models.Model):
    """Конфигурация самолёта (аналог Order)"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Поля заказчика
    customer_name = models.CharField(max_length=200, default="Гость")
    purpose = models.CharField(max_length=200, blank=True, verbose_name="Назначение")
    aircraft_model = models.CharField(max_length=100, blank=True, verbose_name="Модель ВС")
    mm_field = models.CharField(max_length=200, blank=True, verbose_name="М-М поле (особые требования)")
    
    # Финансы
    delivery_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    
    # Связи с пользователями
    creator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='configurations', null=True)
    moderator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='moderated_configs', null=True, blank=True)
    
    # Связь многие-ко-многим
    airplanes = models.ManyToManyField(Airplane, through='AirplaneConfiguration')
    
    class Meta:
        db_table = 'configurations'
        verbose_name = "Конфигурация"
        verbose_name_plural = "Конфигурации"
    
    def __str__(self):
        return f"Конфигурация #{self.id} - {self.customer_name}"
    
    @property
    def total_cost(self):
        """Вычисляемая стоимость (сумма всех позиций)"""
        total = 0
        for item in self.items.all():
            total += item.quantity * float(item.airplane.price)
        return total


class AirplaneConfiguration(models.Model):
    """Связка: самолёт в конфигурации"""
    configuration = models.ForeignKey(Configuration, on_delete=models.RESTRICT, related_name='items')
    airplane = models.ForeignKey(Airplane, on_delete=models.RESTRICT, related_name='config_items')
    quantity = models.PositiveIntegerField(default=1)
    order_index = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    result_field = models.CharField(max_length=255, null=True, blank=True, verbose_name="Вычисляемое поле")
    
    class Meta:
        db_table = 'airplane_configurations'
        verbose_name = "Самолёт в конфигурации"
        verbose_name_plural = "Самолёты в конфигурациях"
        unique_together = ['configuration', 'airplane']
    
    def __str__(self):
        return f"{self.configuration.id} - {self.airplane.model_name} x{self.quantity}"