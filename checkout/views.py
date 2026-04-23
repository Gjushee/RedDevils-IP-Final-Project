import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm


def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required(login_url='/login/')
def checkout(request):
    cart  = _get_cart(request.user)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    profile = getattr(request.user, 'profile', None)
    initial = {
        'full_name': profile.full_name if profile else '',
        'email':     request.user.email,
        'phone':     profile.phone_number if profile else '',
    }

    try:
        role = request.user.profile.role
    except Exception:
        role = 'free'
    is_gold      = role in ('gold', 'admin')
    discount_pct = getattr(settings, 'GOLD_DISCOUNT_PERCENT', 10) if is_gold else 0

    def _item_price(item):
        price = item.product.price
        if is_gold:
            price = round(price * Decimal(str(1 - discount_pct / 100)), 2)
        return price

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = sum(_item_price(i) * i.quantity for i in items)
            order = Order.objects.create(
                user           = request.user,
                full_name      = form.cleaned_data['full_name'],
                email          = form.cleaned_data['email'],
                phone          = form.cleaned_data.get('phone', ''),
                address_line1  = form.cleaned_data['address_line1'],
                address_line2  = form.cleaned_data.get('address_line2', ''),
                city           = form.cleaned_data['city'],
                postcode       = form.cleaned_data['postcode'],
                country        = form.cleaned_data['country'],
                payment_method = 'card',
                status         = 'completed',
                total_amount   = total,
            )

            for item in items:
                OrderItem.objects.create(
                    order        = order,
                    product_name = item.product.name,
                    size         = item.size or '',
                    quantity     = item.quantity,
                    unit_price   = _item_price(item),
                )

            cart.items.all().delete()
            return redirect('checkout:confirmation', order_ref=order.order_ref)
    else:
        form = CheckoutForm(initial=initial)

    display_total   = sum(_item_price(i) * i.quantity for i in items)
    original_total  = cart.total_price
    discount_amount = round(original_total - display_total, 2)

    enriched_items = [
        {
            'item':       i,
            'line_total': round(_item_price(i) * i.quantity, 2),
        }
        for i in items
    ]

    context = {
        'cart':             cart,
        'items':            items,
        'enriched_items':   enriched_items,
        'form':             form,
        'paypal_client_id': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
        'is_gold':          is_gold,
        'discount_pct':     discount_pct,
        'display_total':    display_total,
        'original_total':   original_total,
        'discount_amount':  discount_amount,
    }
    return render(request, 'checkout/checkout.html', context)


@login_required(login_url='/login/')
def confirmation(request, order_ref):
    order = get_object_or_404(Order, order_ref=order_ref, user=request.user)
    return render(request, 'checkout/confirmation.html', {'order': order})


@login_required(login_url='/login/')
@require_POST
def paypal_create_order(request):
    cart = _get_cart(request.user)
    if not cart.items.exists():
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    try:
        import paypalrestsdk
        paypalrestsdk.configure({
            'mode': getattr(settings, 'PAYPAL_MODE', 'sandbox'),
            'client_id':     settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
        })

        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer': {'payment_method': 'paypal'},
            'redirect_urls': {
                'return_url': request.build_absolute_uri('/checkout/paypal/execute/'),
                'cancel_url': request.build_absolute_uri('/checkout/'),
            },
            'transactions': [{
                'amount': {
                    'total':    str(cart.total_price),
                    'currency': 'GBP',
                },
                'description': 'Red Devils Hub Order',
            }],
        })

        if payment.create():
            approval_url = next(
                link.href for link in payment.links if link.rel == 'approval_url'
            )
            return JsonResponse({'approval_url': approval_url})
        else:
            return JsonResponse({'error': str(payment.error)}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required(login_url='/login/')
def paypal_capture(request):
    payment_id = request.GET.get('paymentId')
    payer_id   = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, 'PayPal payment was cancelled.')
        return redirect('checkout:checkout')

    try:
        import paypalrestsdk
        paypalrestsdk.configure({
            'mode': getattr(settings, 'PAYPAL_MODE', 'sandbox'),
            'client_id':     settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
        })

        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({'payer_id': payer_id}):
            cart = _get_cart(request.user)
            billing = request.session.pop('checkout_billing', {})

            order = Order.objects.create(
                user           = request.user,
                full_name      = billing.get('full_name', request.user.get_full_name() or request.user.username),
                email          = billing.get('email', request.user.email),
                phone          = billing.get('phone', ''),
                address_line1  = billing.get('address_line1', '—'),
                address_line2  = billing.get('address_line2', ''),
                city           = billing.get('city', '—'),
                postcode       = billing.get('postcode', '—'),
                country        = billing.get('country', 'United Kingdom'),
                payment_method = 'paypal',
                paypal_order_id= payment_id,
                status         = 'completed',
                total_amount   = cart.total_price,
            )

            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order        = order,
                    product_name = item.product.name,
                    size         = item.size or '',
                    quantity     = item.quantity,
                    unit_price   = item.product.price,
                )

            cart.items.all().delete()
            return redirect('checkout:confirmation', order_ref=order.order_ref)
        else:
            messages.error(request, 'PayPal payment could not be completed.')
            return redirect('checkout:checkout')

    except Exception as e:
        messages.error(request, f'PayPal error: {e}')
        return redirect('checkout:checkout')


@login_required(login_url='/login/')
@require_POST
def save_billing_session(request):
    data = json.loads(request.body)
    request.session['checkout_billing'] = data
    return JsonResponse({'ok': True})


@login_required(login_url='/login/')
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'checkout/order_history.html', {'orders': orders})
