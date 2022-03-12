from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

def store(request, category_slug=None):
    products = Product.objects.all().filter(is_available=True).order_by('id')
    product_count = products.count()
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=categories)
        product_count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    page_products = paginator.get_page(page)
    context = {
        # 'products' : products,
        'products' : page_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    # categories = get_object_or_404(Category, slug=category_slug)
    single_product = get_object_or_404(Product, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product= single_product).exists()
    

    product_gallery = ProductGallery.objects.filter(product_id = single_product.id)
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_gallery': product_gallery
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    products = []
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
            product_count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    page_products = paginator.get_page(page)
    context = {
        # 'products' : products,
        'products' : page_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)
