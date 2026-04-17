from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    """Модель услуги (комплектующей для самолёта)"""
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удалена'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    image_url = models.URLField(null=True, blank=True, verbose_name="URL изображения")
    video_url = models.URLField(null=True, blank=True, verbose_name="URL видео")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Дополнительные поля по вашей предметной области
    width = models.CharField(max_length=50, blank=True, verbose_name="Ширина")
    height = models.CharField(max_length=50, blank=True, verbose_name="Высота")
    depth = models.CharField(max_length=50, blank=True, verbose_name="Глубина")
    material = models.CharField(max_length=100, blank=True, verbose_name="Материал")
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'services'
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class Order(models.Model):
    """Модель заявки (корзина/заказ)"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='orders')
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    moderator = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True, related_name='moderated_orders')
    
    # Рассчитываемое поле (при завершении заявки)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.get_status_display()}"
    
    class Meta:
        db_table = 'orders'
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class OrderService(models.Model):
    """Связь многие-ко-многим: заявки и услуги"""
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    service = models.ForeignKey(Service, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        db_table = 'order_service'
        unique_together = [['order', 'service']]  # Составной уникальный ключ
        verbose_name = "Услуга в заявке"
        verbose_name_plural = "Услуги в заявках"
    
    def __str__(self):
        return f"{self.order.id} - {self.service.name} x{self.quantity}"