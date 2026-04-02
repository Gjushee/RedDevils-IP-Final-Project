from django.contrib import admin
from .models import Category, SubCategory, Player, Product, ProductImage
 
 
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
 
 
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
 
 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
 
 
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'slug')
    list_filter   = ('category',)
    prepopulated_fields = {'slug': ('name',)}
 
 
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'squad_number')
 
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('name', 'subcategory', 'player', 'price', 'stock_quantity', 'access_level', 'is_available')
    list_filter    = ('subcategory__category', 'access_level', 'is_available', 'size')
    search_fields  = ('name', 'brand', 'player__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines        = [ProductImageInline]
    list_editable  = ('price', 'stock_quantity', 'is_available')