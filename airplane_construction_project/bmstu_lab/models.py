from django.db import models
from django.contrib.auth.models import User

class AirplaneProduct(models.Model):
    """Авиационный продукт/комплектующая"""
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
    
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Вес (кг)")
    material = models.CharField(max_length=100, default="Алюминий", verbose_name="Материал")
    manufacturer = models.CharField(max_length=200, default="АвиаЗавод", verbose_name="Производитель")
    
    class Meta:
        db_table = 'airplane_products'
        verbose_name = "Авиапродукт"
        verbose_name_plural = "Авиапродукты"
    
    def __str__(self):
        return self.name


class AirplaneRequest(models.Model):
    """Заявка на комплектацию самолёта"""
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
    
    client_name = models.CharField(max_length=200, default="Гость")
    purpose = models.CharField(max_length=200, blank=True)
    aircraft_model = models.CharField(max_length=100, blank=True)
    special_request = models.CharField(max_length=200, blank=True, verbose_name="Особое пожелание")  # поле по теме
    
    # total_cost - УДАЛЕНО! Будет вычисляться при формировании
    
    creator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='requests', null=True)
    moderator = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='moderated_requests', null=True, blank=True)
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)

    class Meta:
        db_table = 'airplane_requests'
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.client_name}"


class AirplaneRequestItem(models.Model):
    """Позиция заявки (связь продукта с заявкой)"""
    request = models.ForeignKey(AirplaneRequest, on_delete=models.RESTRICT, related_name='items')
    product = models.ForeignKey(AirplaneProduct, on_delete=models.RESTRICT, related_name='request_items')
    quantity = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)  # порядок
    result_field = models.CharField(max_length=255, null=True, blank=True)  # вычисляемое поле из лаб8
    
    class Meta:
        db_table = 'airplane_request_items'
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявок"
        unique_together = ['request', 'product']
    
    def __str__(self):
        return f"{self.request.id} - {self.product.name} x{self.quantity}"