from django.db import models
from django.conf import settings  
from django.utils.text import slugify
 
 
class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
 
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
 
class SubCategory(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name        = models.CharField(max_length=100)
    slug        = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
 
    class Meta:
        verbose_name_plural = 'SubCategories'
        unique_together = ('category', 'slug')
        ordering = ['name']
 
    def __str__(self):
        return f"{self.category.name} → {self.name}"
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
 
class Player(models.Model):
    name         = models.CharField(max_length=100)
    position     = models.CharField(max_length=50, blank=True)
    squad_number = models.PositiveIntegerField(null=True, blank=True)
    image        = models.ImageField(upload_to='players/', blank=True, null=True)
    bio          = models.TextField(blank=True)
 
    class Meta:
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
 
class Product(models.Model):
    ACCESS_FREE = 'free'
    ACCESS_RED  = 'red'
    ACCESS_GOLD = 'gold'
    ACCESS_CHOICES = [
        (ACCESS_FREE, 'Free'),
        (ACCESS_RED,  'Red Members'),
        (ACCESS_GOLD, 'Gold Members'),
    ]
 
    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
        ('ONE', 'One Size'),
    ]
 
    subcategory         = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    player              = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name                = models.CharField(max_length=200)
    slug                = models.SlugField(max_length=200, unique=True, blank=True)
    description         = models.TextField(blank=True)
    price               = models.DecimalField(max_digits=8, decimal_places=2)
    stock_quantity      = models.PositiveIntegerField(default=0)
    colour              = models.CharField(max_length=50, blank=True)
    size                = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True)
    brand               = models.CharField(max_length=100, blank=True)
    season              = models.CharField(max_length=20, blank=True)
    access_level        = models.CharField(max_length=10, choices=ACCESS_CHOICES, default=ACCESS_FREE)
    is_available        = models.BooleanField(default=True)
    created_at          = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return self.name
 
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
 
    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()
 
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
 
 
class ProductImage(models.Model):
    product    = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    alt_text   = models.CharField(max_length=200, blank=True)
 
    def __str__(self):
        return f"Image for {self.product.name}"


class ProductRating(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating  = models.PositiveSmallIntegerField()  # 1-5

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} → {self.product.name}: {self.rating}★"
