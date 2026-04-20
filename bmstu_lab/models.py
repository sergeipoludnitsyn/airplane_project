from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удалена'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    width = models.CharField(max_length=50, blank=True)
    height = models.CharField(max_length=50, blank=True)
    depth = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'services'

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    
    session_key = models.CharField(max_length=40, blank=True, null=True)  # 👈 ДОБАВИТЬ ЭТО
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    # creator = models.ForeignKey(User, on_delete=models.RESTRICT)  # УДАЛИТЬ
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # moderator = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)  # УДАЛИТЬ
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        # Удалить constraint unique_draft_per_user

class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.RESTRICT)
    service = models.ForeignKey(Service, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'order_service'
        unique_together = [['order', 'service']]