from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, pk=product_id)

    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass
        
        
        try:
            cart_items = CartItem.objects.filter(product=product, user=current_user,)
            cart_item = None
            for x in cart_items:
                if list(x.variations.all())==product_variation:
                    cart_item = x
                    break
            if cart_item==None:
                CartItem.objects.get(product=None,  user=current_user,)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()
        return redirect('cart')




    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()
        try:
            cart_items = CartItem.objects.filter(product=product, cart=cart,)
            cart_item = None
            for x in cart_items:
                if list(x.variations.all())==product_variation:
                    cart_item = x
                    break
            if cart_item==None:
                CartItem.objects.get(product=None, cart=cart,)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()
        return redirect('cart')


def remove_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, pk=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request):
    cart_items = []
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity':quantity,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url= 'login')
def checkout(request):
    cart_items = []
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    try:
        cart_items = CartItem.objects.filter(user=request.user)
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity':quantity,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context)
