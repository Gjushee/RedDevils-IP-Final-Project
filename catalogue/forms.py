from django import forms
from .models import Category, SubCategory, Product, ProductImage


class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image':       forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model  = SubCategory
        fields = ['category', 'name', 'description']
        widgets = {
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = [
            'subcategory', 'player', 'name', 'description',
            'price', 'stock_quantity', 'colour', 'size',
            'brand', 'season', 'access_level', 'is_available',
        ]
        widgets = {
            'subcategory':    forms.Select(attrs={'class': 'form-select'}),
            'player':         forms.Select(attrs={'class': 'form-select'}),
            'name':           forms.TextInput(attrs={'class': 'form-control'}),
            'description':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price':          forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'colour':         forms.TextInput(attrs={'class': 'form-control'}),
            'size':           forms.Select(attrs={'class': 'form-select'}),
            'brand':          forms.TextInput(attrs={'class': 'form-control'}),
            'season':         forms.TextInput(attrs={'class': 'form-control'}),
            'access_level':   forms.Select(attrs={'class': 'form-select'}),
            'is_available':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model  = ProductImage
        fields = ['image', 'is_primary', 'alt_text']
        widgets = {
            'image':    forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
        }
