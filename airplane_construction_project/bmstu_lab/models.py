from django.db import models

class Service(models.Model):
    """Модель услуги (комплектующей для самолёта)"""
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удалена'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Стоимость")
    image_url = models.URLField(null=True, blank=True, verbose_name="URL изображения")
    video_url = models.URLField(null=True, blank=True, verbose_name="URL видео")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Поля по предметной области
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Вес (кг)")
    material = models.CharField(max_length=100, default="Алюминий", verbose_name="Материал")
    manufacturer = models.CharField(max_length=200, default="АвиаЗавод", verbose_name="Производитель")
    
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
    
    # Основные поля (NOT NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Дополнительные поля (NULLABLE)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Поле "для кого"
    client_name = models.CharField(max_length=200, verbose_name="Для кого (организация/ФИО)", default="Гость")
    
    # Поле по предметной области
    purpose = models.CharField(max_length=200, verbose_name="Цель использования", blank=True)
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.client_name}"
    
    class Meta:
        db_table = 'orders'
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class OrderService(models.Model):
    """Связь многие-ко-многим: заявки и услуги"""
    order = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name='order_services')
    service = models.ForeignKey(Service, on_delete=models.RESTRICT, related_name='order_services')
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        db_table = 'order_services'
        verbose_name = "Услуга в заявке"
        verbose_name_plural = "Услуги в заявках"
        unique_together = ['order', 'service']  # Составной уникальный ключ
    
    def __str__(self):
        return f"{self.order.id} - {self.service.name} x{self.quantity}"