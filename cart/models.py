from django.db import models
from django.contrib.auth.models import User
from catalogue.models import Product


class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart      = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product   = models.ForeignKey(Product, on_delete=models.CASCADE)
    size      = models.CharField(max_length=10, blank=True)
    quantity  = models.PositiveIntegerField(default=1)
    added_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'size')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.size or 'No size'})"

    @property
    def line_total(self):
        return self.product.price * self.quantity


class WishlistItem(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} → {self.product.name}'
