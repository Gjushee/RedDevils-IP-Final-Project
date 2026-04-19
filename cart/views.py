import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from catalogue.models import Product
from .models import Cart, CartItem, WishlistItem


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# ──────────────────────────────────────────────
# ADD TO CART
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    size    = request.POST.get('size', '')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not product.is_in_stock:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Out of stock.'})
        messages.error(request, 'This product is out of stock.')
        return redirect('catalogue:product_detail', slug=product.slug)

    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, size=size,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()

    if is_ajax:
        return JsonResponse({
            'success':     True,
            'total_items': cart.total_items,
            'total_price': str(cart.total_price),
            'message':     f'{product.name} added to cart.',
        })

    messages.success(request, f'{product.name} added to your cart.')
    return redirect('catalogue:product_detail', slug=product.slug)


# ──────────────────────────────────────────────
# UPDATE QUANTITY (+/-)
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
@require_POST
def update_quantity(request, item_id):
    item    = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    action  = request.POST.get('action')  # 'increase' or 'decrease'
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
            if is_ajax:
                cart = _get_or_create_cart(request.user)
                return JsonResponse({
                    'success':     True,
                    'removed':     True,
                    'item_id':     item_id,
                    'total_items': cart.total_items,
                    'total_price': str(cart.total_price),
                })
            return redirect('cart:cart_detail')

    cart = item.cart
    if is_ajax:
        return JsonResponse({
            'success':     True,
            'removed':     False,
            'item_id':     item_id,
            'quantity':    item.quantity,
            'line_total':  str(item.line_total),
            'total_items': cart.total_items,
            'total_price': str(cart.total_price),
        })

    return redirect('cart:cart_detail')


# ──────────────────────────────────────────────
# REMOVE ITEM
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
@require_POST
def remove_item(request, item_id):
    item    = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    cart    = item.cart
    item.delete()

    if is_ajax:
        return JsonResponse({
            'success':     True,
            'item_id':     item_id,
            'total_items': cart.total_items,
            'total_price': str(cart.total_price),
        })

    messages.success(request, 'Item removed from cart.')
    return redirect('cart:cart_detail')


# ──────────────────────────────────────────────
# CLEAR ENTIRE CART
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
@require_POST
def clear_cart(request):
    cart = _get_or_create_cart(request.user)
    cart.items.all().delete()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'total_items': 0, 'total_price': '0.00'})
    messages.success(request, 'Cart cleared.')
    return redirect('cart:cart_detail')


# ──────────────────────────────────────────────
# CART DETAIL PAGE
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
def cart_detail(request):
    cart  = _get_or_create_cart(request.user)
    items = cart.items.select_related('product').all()
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'items': items})


# ──────────────────────────────────────────────
# CART SUMMARY (JSON — used by the floating panel)
# ──────────────────────────────────────────────
@login_required(login_url='/login/')
def cart_summary(request):
    cart  = _get_or_create_cart(request.user)
    items = []
    for item in cart.items.select_related('product').all():
        img = item.product.primary_image
        items.append({
            'id':         item.pk,
            'name':       item.product.name,
            'size':       item.size or '—',
            'price':      str(item.product.price),
            'line_total': str(item.line_total),
            'quantity':   item.quantity,
            'image':      img.image.url if img else '',
            'slug':       item.product.slug,
        })
    return JsonResponse({
        'items':       items,
        'total_items': cart.total_items,
        'total_price': str(cart.total_price),
    })


# ──────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────

@login_required
def wishlist_page(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'cart/wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        in_wishlist = False
    else:
        in_wishlist = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})

    return redirect(request.META.get('HTTP_REFERER', 'cart:wishlist_page'))
