import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .forms import CheckoutForm
from .models import Order, OrderItem
from cart.models import Cart


def _cart_or_redirect(request):
    try:
        cart = request.user.cart
        if cart.items.count() == 0:
            return None, redirect('cart:cart_detail')
        return cart, None
    except Cart.DoesNotExist:
        return None, redirect('cart:cart_detail')


@login_required
def checkout(request):
    cart, redir = _cart_or_redirect(request)
    if redir:
        return redir

    profile = getattr(request.user, 'profile', None)
    initial = {}
    if profile:
        initial = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email':     request.user.email,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            order = Order.objects.create(
                user           = request.user,
                full_name      = d['full_name'],
                email          = d['email'],
                phone          = d.get('phone', ''),
                address_line1  = d['address_line1'],
                address_line2  = d.get('address_line2', ''),
                city           = d['city'],
                postcode       = d['postcode'],
                country        = d['country'],
                payment_method = 'card',
                status         = 'completed',
                total_amount   = cart.total_price,
            )
            for item in cart.items.all():
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
        form = CheckoutForm(initial=initial)

    paypal_client_id = getattr(settings, 'PAYPAL_CLIENT_ID', '')
    return render(request, 'checkout/checkout.html', {
        'form':             form,
        'cart':             cart,
        'items':            cart.items.select_related('product').all(),
        'paypal_client_id': paypal_client_id,
    })


@login_required
def confirmation(request, order_ref):
    order = get_object_or_404(Order, order_ref=order_ref, user=request.user)
    return render(request, 'checkout/confirmation.html', {'order': order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related('items').order_by('-created_at')
    return render(request, 'checkout/order_history.html', {'orders': orders})


@login_required
def save_billing_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            request.session['billing'] = data
            return JsonResponse({'ok': True})
        except Exception:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def paypal_create_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        import paypalrestsdk
        paypalrestsdk.configure({
            'mode':         getattr(settings, 'PAYPAL_MODE', 'sandbox'),
            'client_id':    settings.PAYPAL_CLIENT_ID,
            'client_secret':settings.PAYPAL_CLIENT_SECRET,
        })
        cart = request.user.cart
        payment = paypalrestsdk.Payment({
            'intent': 'sale',
            'payer':  {'payment_method': 'paypal'},
            'transactions': [{'amount': {'total': str(cart.total_price), 'currency': 'GBP'}}],
            'redirect_urls': {
                'return_url': request.build_absolute_uri('/checkout/paypal/execute/'),
                'cancel_url': request.build_absolute_uri('/checkout/checkout/'),
            },
        })
        if payment.create():
            return JsonResponse({'order_id': payment.id})
        return JsonResponse({'error': str(payment.error)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def paypal_capture(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        import paypalrestsdk
        data     = json.loads(request.body)
        order_id = data.get('order_id')
        payment  = paypalrestsdk.Payment.find(order_id)
        payer_id = payment.payer.payer_info.payer_id
        if payment.execute({'payer_id': payer_id}):
            billing = request.session.pop('billing', {})
            cart    = request.user.cart
            order   = Order.objects.create(
                user            = request.user,
                full_name       = billing.get('full_name', ''),
                email           = billing.get('email', ''),
                phone           = billing.get('phone', ''),
                address_line1   = billing.get('address_line1', ''),
                address_line2   = billing.get('address_line2', ''),
                city            = billing.get('city', ''),
                postcode        = billing.get('postcode', ''),
                country         = billing.get('country', 'United Kingdom'),
                payment_method  = 'paypal',
                paypal_order_id = order_id,
                status          = 'completed',
                total_amount    = cart.total_price,
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order        = order,
                    product_name = item.product.name,
                    size         = item.size or '',
                    quantity     = item.quantity,
                    unit_price   = item.product.price,
                )
            cart.items.all().delete()
            return JsonResponse({'redirect_url': f'/checkout/confirmation/{order.order_ref}/'})
        return JsonResponse({'error': 'Payment execution failed'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
