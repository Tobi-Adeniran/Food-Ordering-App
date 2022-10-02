from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from .models import MenuItem, Category, OrderModel, Payment
from . import forms
from django.http.response import HttpResponse
from django.http.request import HttpRequest


class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')

class Order(View):
    def get(self, request, *args, **kwargs):
        #get every item from each category
        appetizers = MenuItem.objects.filter(category__name__contains = 'Appetizer')
        desserts = MenuItem.objects.filter(category__name__contains = 'Dessert')
        dishes = MenuItem.objects.filter(category__name__contains = 'Dish')
        drinks = MenuItem.objects.filter(category__name__contains = 'Drink')

        context = {
            'appetizers': appetizers,
            'desserts': desserts,
            'drinks': drinks,
            'dishes': dishes,
        }

        return render(request, 'customer/order.html', context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')


        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price,
            }

            order_items['items'].append(item_data)

            price = 0
            item_ids = []

        for item in order_items['items']:
                price += item['price']
                item_ids.append(item['id'])

        order = OrderModel.objects.create(
            price=price,
            name=name,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
            )
        order.items.add(*item_ids)

        body = ('Thank you again for your order, your meal is being made and will be delivered to you shortly!\n'
        f'Your Total: {price}\n'
        'Thank you again for your order!')

        #email confirmation message
        send_mail(
            'Thank yoou for your order!',
            body,
            'example@gmail.com',
            [email],
            fail_silently=False
        )

        context = {
                'items': order_items['items'],
                'price': price
            }

        return render(request, 'customer/order_confirmation.html', context)

def initiate_payment(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        payment_form = forms.PaymentForm(request.POST)
        if payment_form:
            payment = payment_form.save()
            return render(request, 'customer/make_payment.html', {'payment': payment, 'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY})
    else:
        payment_form = forms.PaymentForm()
    return render(request, 'customer/initiate_payment.html', {'payment_form': payment_form})

def verify_payment(request: HttpRequest, ref: str) -> HttpResponse:
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()
    if verified:
        messages.success(request, "Verification Successful")
    else:
        messages.error(request, "Verification Failed")
    return redirect('initiate-payment')