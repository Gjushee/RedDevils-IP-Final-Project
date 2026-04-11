import uuid
from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
    ]
    PAYMENT_CHOICES = [
        ('card',   'Demo Card'),
        ('paypal', 'PayPal'),
    ]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_ref      = models.CharField(max_length=20, unique=True, blank=True)
    full_name      = models.CharField(max_length=200)
    email          = models.EmailField()
    phone          = models.CharField(max_length=20, blank=True)
    address_line1  = models.CharField(max_length=200)
    address_line2  = models.CharField(max_length=200, blank=True)
    city           = models.CharField(max_length=100)
    postcode       = models.CharField(max_length=20)
    country        = models.CharField(max_length=100, default='United Kingdom')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='card')
    paypal_order_id= models.CharField(max_length=100, blank=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_ref:
            self.order_ref = 'RDH-' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_ref


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)
    size         = models.CharField(max_length=10, blank=True)
    quantity     = models.PositiveIntegerField(default=1)
    unit_price   = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'
