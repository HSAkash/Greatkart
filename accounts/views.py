from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# email
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse

#session
from carts.views import _cart_id
from carts.models import Cart, CartItem

#
import requests

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            user = Account.objects.create_user(
                first_name= first_name,
                last_name= last_name,
                username= username,
                email= email,
                password= password,
            )
            user.phone_number = phone_number
            # user.set_password(password)
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            email = EmailMessage(  
                mail_subject, message, to=[to_email]  
            )
            email.send()


            # messages.success(request, 'Thank you for registering with us.We have sent you  a verifications email to your email address.Please verify it.')
            return redirect(f'/accounts/login/?command=verification&email={email}')
    else:
        form = RegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    user_cart_item = CartItem.objects.filter(user=user)
                    if user_cart_item:
                        for item in cart_item:
                            item_product = item.product
                            item_variations = list(item.variations.all())
                            item_quantity = item.quantity
                            flag = True
                            for user_item in user_cart_item:
                                if user_item.product == item_product and list(user_item.variations.all()) == item_variations:
                                    user_item.quantity += item_quantity
                                    user_item.save()
                                    flag = False
                                    break
                            if flag:
                                item.user = user
                                item.save()
                    else:
                        for item in cart_item:
                            item.user = user
                            item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'you are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                pass
            return redirect('home')
        messages.error(request, 'Invalid login credentials')
        return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url= 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Your are loged out.')
    return redirect('login')






def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64).decode('utf8')) 
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None  
    if user is not None and default_token_generator.check_token(user, token):  
        user.is_active = True  
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')  
    else:  
        messages.error(request, 'Invalid activation link')
        return redirect('register')



@login_required(login_url= 'login')
def dashboard(request):
    context = {}
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            print(user)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            email = EmailMessage(  
                mail_subject, message, to=[to_email]  
            )
            email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')
    context = {}
    return render(request, 'accounts/forgotPassword.html', context)

def resetpassword_validate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64).decode('utf8')) 
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):  
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')  
    else:  
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if not request.session.get('uid'):
        return redirect('forgotPassword')
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if confirm_password == password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    context = {}
    return render(request, 'accounts/resetPassword.html', context)

    