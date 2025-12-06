from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Review
from .forms import ReviewForm, ProductForm
from barter.utils import ai_suggestions
from django.db.models import Q



def product_detail(request, product_id):
    # Get the product or 404
    product = get_object_or_404(Product, id=product_id)

    # Reviews for this product
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    # Average rating
    if reviews.exists():
        avg_rating = round(sum([r.rating for r in reviews]) / reviews.count(), 1)  # 1 decimal place
    else:
        avg_rating = 0

    # Suggested products (same category, exclude current product)
    suggested_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    # Handle review form submission
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'suggested_products': suggested_products,
        'review_form': review_form,
    }
    return render(request, 'products/product_detail.html', context)


# ----------------------------
# List All Products
# ----------------------------
def all_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'products/all_products.html', {'products': products})


# ----------------------------
# Add Product
# ----------------------------
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('all_products')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


# ------------------------------
# delete product
# --------------------------------
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.delete()
        return redirect('my_products') 


# ----------------------------
# My Products
# ----------------------------
@login_required
def my_products(request):
    products = Product.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'products/my_products.html', {'products': products})


# ----------------------------
#  Product List
# ----------------------------

def product_list(request):
    query = request.GET.get('q', '')  # search keyword
    products = Product.objects.all()

    # Search by title or description
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'products/product_list.html', context)


@login_required
def toggle_favorite(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user

    if product in user.favorites.all():
        user.favorites.remove(product)
        status = 'removed'
    else:
        user.favorites.add(product)
        status = 'added'

    # Return JSON including new count
    return JsonResponse({
        'status': status,
        'count': user.favorites.count()
    })


@login_required
def wishlist(request):
    user = request.user
    favorite_products = user.favorites.all()
    return render(request, 'products/wishlist.html', {'favorite_products': favorite_products})

