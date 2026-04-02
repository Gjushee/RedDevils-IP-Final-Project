from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, SubCategory, Product, Player
 
 
def catalogue(request):
    products    = Product.objects.filter(is_available=True).select_related('subcategory__category', 'player')
    categories  = Category.objects.prefetch_related('subcategories')
    players     = Player.objects.all()
 
    # ── Basic search (name or player/collection) ──────────────
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(player__name__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query)
        )
 
    # ── Advanced filters ──────────────────────────────────────
    category_slug    = request.GET.get('category', '')
    subcategory_slug = request.GET.get('subcategory', '')
    player_id        = request.GET.get('player', '')
    colour           = request.GET.get('colour', '').strip()
    size             = request.GET.get('size', '')
    price_min        = request.GET.get('price_min', '').strip()
    price_max        = request.GET.get('price_max', '').strip()
    in_stock         = request.GET.get('in_stock', '')
    access_level     = request.GET.get('access_level', '')
 
    if category_slug:
        products = products.filter(subcategory__category__slug=category_slug)
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    if player_id:
        products = products.filter(player__id=player_id)
    if colour:
        products = products.filter(colour__icontains=colour)
    if size:
        products = products.filter(size=size)
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
    if in_stock:
        products = products.filter(stock_quantity__gt=0)
    if access_level:
        products = products.filter(access_level=access_level)
 
    # ── Membership gate — hide premium products from lower tiers ──
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
        except Exception:
            role = 'free'
    else:
        role = 'anonymous'
 
    if role not in ('gold', 'admin'):
        products = products.exclude(access_level='gold')
    if role not in ('red', 'gold', 'admin'):
        products = products.exclude(access_level='red')
 
    # ── Collect unique colours for the filter dropdown ──
    colours = (
        Product.objects.filter(is_available=True)
        .exclude(colour='')
        .values_list('colour', flat=True)
        .distinct()
        .order_by('colour')
    )
 
    context = {
        'products':        products,
        'categories':      categories,
        'players':         players,
        'colours':         colours,
        'size_choices':    Product.SIZE_CHOICES,
        'query':           query,
        'selected_cat':    category_slug,
        'selected_subcat': subcategory_slug,
        'selected_player': player_id,
        'selected_colour': colour,
        'selected_size':   size,
        'price_min':       price_min,
        'price_max':       price_max,
        'in_stock':        in_stock,
        'access_level':    access_level,
        'total_results':   products.count(),
    }
    return render(request, 'catalogue/catalogue.html', context)
 
 
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
 
    # Membership gate for premium products
    if product.access_level != 'free':
        if not request.user.is_authenticated:
            from django.contrib import messages
            messages.warning(request, 'Please log in to view this product.')
            return render(request, 'catalogue/product_locked.html', {'product': product})
        try:
            role = request.user.profile.role
        except Exception:
            role = 'free'
 
        if product.access_level == 'gold' and role not in ('gold', 'admin'):
            return render(request, 'catalogue/product_locked.html', {'product': product})
        if product.access_level == 'red' and role not in ('red', 'gold', 'admin'):
            return render(request, 'catalogue/product_locked.html', {'product': product})
 
    # Related products — same subcategory, excluding current
    related = (
        Product.objects.filter(subcategory=product.subcategory, is_available=True)
        .exclude(pk=product.pk)[:4]
    )
 
    context = {
        'product': product,
        'related': related,
    }
    return render(request, 'catalogue/product_detail.html', context)