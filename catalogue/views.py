from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Category, SubCategory, Product, Player, ProductImage, ProductRating
from .forms import CategoryForm, SubCategoryForm, ProductForm, ProductImageForm


def _gold_price(price):
    pct = getattr(settings, 'GOLD_DISCOUNT_PERCENT', 10)
    return round(float(price) * (1 - pct / 100), 2)


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

    is_gold = role in ('gold', 'admin')

    # ── Recommendations — based on recently viewed products ───────
    recommended = []
    viewed_ids  = request.session.get('recently_viewed', [])
    no_filters  = not any([query, category_slug, subcategory_slug,
                           player_id, colour, size, price_min, price_max])
    if viewed_ids and no_filters:
        base_qs = Product.objects.filter(is_available=True).exclude(pk__in=viewed_ids)
        if role not in ('gold', 'admin'):
            base_qs = base_qs.exclude(access_level='gold')
        if role not in ('red', 'gold', 'admin'):
            base_qs = base_qs.exclude(access_level='red')

        # 1st priority: same subcategory
        subcat_ids = list(
            Product.objects.filter(pk__in=viewed_ids)
            .values_list('subcategory_id', flat=True)
        )
        rec_list = list(
            base_qs.filter(subcategory_id__in=subcat_ids)
            .select_related('subcategory__category', 'player')
            .distinct()[:4]
        )

        # 2nd priority: same category (fill remaining slots)
        if len(rec_list) < 4:
            cat_ids = list(
                Product.objects.filter(pk__in=viewed_ids)
                .values_list('subcategory__category_id', flat=True)
            )
            already = [p.pk for p in rec_list]
            extra = list(
                base_qs.filter(subcategory__category_id__in=cat_ids)
                .exclude(pk__in=already)
                .select_related('subcategory__category', 'player')
                .distinct()[:4 - len(rec_list)]
            )
            rec_list += extra

        # 3rd priority: anything available (fill remaining slots)
        if len(rec_list) < 4:
            already = [p.pk for p in rec_list]
            extra = list(
                base_qs.exclude(pk__in=already)
                .select_related('subcategory__category', 'player')
                .order_by('?')[:4 - len(rec_list)]
            )
            rec_list += extra

        recommended = rec_list

    # Wishlist ids for heart button state
    wishlist_ids = set()
    if request.user.is_authenticated:
        from cart.models import WishlistItem
        wishlist_ids = set(
            WishlistItem.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
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
        'is_gold':         is_gold,
        'discount_pct':    getattr(settings, 'GOLD_DISCOUNT_PERCENT', 10),
        'wishlist_ids':    wishlist_ids,
        'recommended':     recommended,
    }
    return render(request, 'catalogue/catalogue.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)

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

    # ── Track recently viewed in session ─────────────────────────
    viewed = request.session.get('recently_viewed', [])
    if product.pk not in viewed:
        viewed.insert(0, product.pk)
    request.session['recently_viewed'] = viewed[:5]
    request.session.modified = True

    related = (
        Product.objects.filter(subcategory=product.subcategory, is_available=True)
        .exclude(pk=product.pk)[:4]
    )

    try:
        role = request.user.profile.role if request.user.is_authenticated else 'free'
    except Exception:
        role = 'free'
    is_gold = role in ('gold', 'admin')

    in_wishlist = False
    if request.user.is_authenticated:
        from cart.models import WishlistItem
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    rating_agg   = product.ratings.aggregate(avg=Avg('rating'))
    avg_rating   = round(rating_agg['avg'], 1) if rating_agg['avg'] else 0
    rating_count = product.ratings.count()
    user_rating  = None
    if request.user.is_authenticated:
        r = ProductRating.objects.filter(user=request.user, product=product).first()
        user_rating = r.rating if r else None

    context = {
        'product':      product,
        'related':      related,
        'is_gold':      is_gold,
        'discount_pct': getattr(settings, 'GOLD_DISCOUNT_PERCENT', 10),
        'gold_price':   _gold_price(product.price) if is_gold else None,
        'in_wishlist':  in_wishlist,
        'avg_rating':   avg_rating,
        'rating_count': rating_count,
        'user_rating':  user_rating,
    }
    return render(request, 'catalogue/product_detail.html', context)


@require_POST
def clear_viewed(request):
    request.session.pop('recently_viewed', None)
    return redirect('catalogue:catalogue')


@login_required
@require_POST
def rate_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    try:
        rating_val = int(request.POST.get('rating', 0))
        if not 1 <= rating_val <= 5:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid rating'}, status=400)

    ProductRating.objects.update_or_create(
        user=request.user, product=product,
        defaults={'rating': rating_val}
    )
    avg   = product.ratings.aggregate(avg=Avg('rating'))['avg'] or 0
    count = product.ratings.count()
    return JsonResponse({
        'success':     True,
        'user_rating': rating_val,
        'avg_rating':  round(avg, 1),
        'count':       count,
    })


# ─────────────────────────────────────────────────────────────
# ADMIN HELPERS & CRUD
# ─────────────────────────────────────────────────────────────

def _admin_check(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in.')
        return redirect('register:login')
    try:
        if not request.user.profile.is_admin():
            messages.error(request, 'Access denied. Admin only.')
            return redirect('core:home')
    except Exception:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    return None


# ── Products ──────────────────────────────────────────────────

def admin_product_list(request):
    guard = _admin_check(request)
    if guard:
        return guard
    products = Product.objects.select_related('subcategory__category').order_by('-created_at')
    return render(request, 'catalogue/admin_products.html', {'products': products})


def admin_product_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    if request.method == 'POST':
        form     = ProductForm(request.POST)
        img_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            if img_form.is_valid() and request.FILES.get('image'):
                img            = img_form.save(commit=False)
                img.product    = product
                img.is_primary = True
                img.save()
            messages.success(request, f'Product "{product.name}" added.')
            return redirect('catalogue:admin_product_list')
    else:
        form     = ProductForm()
        img_form = ProductImageForm()
    return render(request, 'catalogue/admin_product_form.html', {
        'form': form, 'img_form': img_form, 'action': 'Add'
    })


def admin_product_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form     = ProductForm(request.POST, instance=product)
        img_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if img_form.is_valid() and request.FILES.get('image'):
                img            = img_form.save(commit=False)
                img.product    = product
                img.is_primary = True
                img.save()
            messages.success(request, f'Product "{product.name}" updated.')
            return redirect('catalogue:admin_product_list')
    else:
        form     = ProductForm(instance=product)
        img_form = ProductImageForm()
    return render(request, 'catalogue/admin_product_form.html', {
        'form': form, 'img_form': img_form, 'product': product, 'action': 'Edit'
    })


def admin_product_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('catalogue:admin_product_list')
    return render(request, 'catalogue/admin/product_confirm_delete.html', {'product': product})


# ── Categories ────────────────────────────────────────────────

def admin_category_list(request):
    guard = _admin_check(request)
    if guard:
        return guard
    categories = Category.objects.prefetch_related('subcategories').order_by('name')
    return render(request, 'catalogue/admin_categories.html', {'categories': categories})


def admin_category_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Category "{cat.name}" added.')
            return redirect('catalogue:admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'catalogue/admin_category_form.html', {'form': form, 'action': 'Add'})


def admin_category_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{cat.name}" updated.')
            return redirect('catalogue:admin_category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'catalogue/admin_category_form.html', {'form': form, 'cat': cat, 'action': 'Edit'})


def admin_category_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('catalogue:admin_category_list')
    return render(request, 'catalogue/admin/category_confirm_delete.html', {'cat': cat})


# ── Subcategories ─────────────────────────────────────────────

def admin_subcategory_add(request):
    guard = _admin_check(request)
    if guard:
        return guard
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            sub = form.save()
            messages.success(request, f'Subcategory "{sub.name}" added.')
            return redirect('catalogue:admin_category_list')
    else:
        form = SubCategoryForm()
    return render(request, 'catalogue/admin/subcategory_form.html', {'form': form, 'action': 'Add'})


def admin_subcategory_edit(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    sub = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subcategory "{sub.name}" updated.')
            return redirect('catalogue:admin_category_list')
    else:
        form = SubCategoryForm(instance=sub)
    return render(request, 'catalogue/admin/subcategory_form.html', {'form': form, 'sub': sub, 'action': 'Edit'})


def admin_subcategory_delete(request, pk):
    guard = _admin_check(request)
    if guard:
        return guard
    sub = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        name = sub.name
        sub.delete()
        messages.success(request, f'Subcategory "{name}" deleted.')
        return redirect('catalogue:admin_category_list')
    return render(request, 'catalogue/admin/subcategory_confirm_delete.html', {'sub': sub})
