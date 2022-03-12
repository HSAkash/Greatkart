from django import forms
from .models import Payment, Order, OrderProduct


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'post_code',
            'country',
            'order_note',
        )