from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from .forms import OrderForm
import time
from .models import Payment, Order, OrderProduct



@login_required(login_url= 'login')
def payments(request):
    context = {}
    return render(request, 'orders/payments.html', context)









@login_required(login_url= 'login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0 :
        return redirect('store')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        # print(request.POST)
        # print(form.errors)
        if form.is_valid():
            data = Order()
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.post_code = form.cleaned_data['post_code']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.user = current_user


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

            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #Generate order number
            order_number = f"{int(time.time()*10000000)}{data.id}"
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order':order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }

            return render(request, 'orders/payments.html', context)
    
    return redirect('checkout')




