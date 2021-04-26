from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Cart, OrderPlaced, Customer
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        topwear = Product.objects.filter(category='TW')
        bottomwear = Product.objects.filter(category='BW')
        footwear = Product.objects.filter(category='FW')
        mobiles = Product.objects.filter(category='M')
        laptops = Product.objects.filter(category='L')
        return render(request, 'app/home.html',
                      {'topwears': topwear, 'bottomwears': bottomwear, 'footwears': footwear,
                       'mobiles': mobiles, 'laptops': laptops})


def search(request):
    template = 'app/search.html'
    query = request.GET.get('q')
    result = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) )
    context = {'products': result}
    if not query:
        return redirect('home')
    return render(request, template, context)
    

@login_required()
def show_cart_item(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    return render(request, 'app/home.html', {'cart_item': cart})


class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_exist_in_cart = False
        if request.user.is_authenticated:
            item_exist_in_cart = Cart.objects.filter(Q(user=request.user) & Q(product=product.id)).exists()
        return render(request, 'app/productdetail.html', {'product': product, 'item_exist_in_cart': item_exist_in_cart})


@login_required()
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')


@login_required()
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount+shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': totalamount, 'amount': amount})
        else:
            return render(request, 'app/emptycart.html')


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'amount': amount,
            'quantity':  c.quantity,
            'totalamount': amount+shipping_amount,
        }
    return JsonResponse(data)


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'amount': amount,
            'quantity': c.quantity,
            'totalamount': amount+ shipping_amount,
        }
    return JsonResponse(data)


def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount,
        }
    return JsonResponse(data)


def buy_now(request):
    return render(request, 'app/buynow.html')


@login_required
def address(request):
    form = Customer.objects.filter(user=request.user)

    return render(request, 'app/address.html', {'form': form, 'active': 'btn-primary'})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)

    return render(request, 'app/orders.html', {'op': op})


def mobile(request, data=None):
    if data is None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'oneplus' or data == 'Apple' or data == 'asus':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=50000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=50000)
    return render(request, 'app/mobile.html', {'mobiles': mobiles})


def laptop(request, data=None):
    if data is None:
        laptops = Product.objects.filter(category='L')
    elif data == 'asus' or data == 'Apple' or data == 'acer':
        laptops = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt=100000)
    elif data == 'above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt=100000)
    return render(request, 'app/laptops.html', {'laptops': laptops})


def topwear(request, data=None):
    if data is None:
        topwear = Product.objects.filter(category='TW')
    elif data == 'gap' or data == 'wrangler' or data == 'arrow':
        topwear = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'below':
        topwear = Product.objects.filter(category='TW').filter(discounted_price__lt=1000)
    elif data == 'above':
        topwear = Product.objects.filter(category='TW').filter(discounted_price__gt=1000)
    return render(request, 'app/topwear.html', {'topwears': topwear})


def bottomwear(request, data=None):
    if data is None:
        bottomwear = Product.objects.filter(category='BW')
    elif data == 'levis' or data == 'tommyhilfigher' or data == 'peterengland' or data == 'wrangler'\
            or data == 'spykar' or data == 'parkavenue':
        bottomwear = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'below':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__lt=1000)
    elif data == 'above':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__gt=1000)
    elif data == 'above1500':
        bottomwear = Product.objects.filter(category='BW').filter(discounted_price__gt=1500)
    return render(request, 'app/bottomwear.html', {'bottomwears': bottomwear})


def footwear(request, data=None):
    if data is None:
        footwear = Product.objects.filter(category='FW')
    elif data == 'leecooper' or data == 'adidas' or data == 'woodland' or data == 'nike' or data == 'blackfog':
        footwear = Product.objects.filter(category='FW').filter(brand=data)
    return render(request, 'app/footwear.html', {'footwears': footwear})


def audio(request):
    audio = Product.objects.filter(category='A')
    return render(request, 'app/audio.html', {'audio': audio})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations registered successfully !!")
            form.save('registration')
        return render(request, 'app/customerregistration.html', {'form': form})


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == user]
    if cart:
        for p in cart_product:
            temp_amount = (p.quantity * p.product.discounted_price)
            amount += temp_amount
            total_amount = amount + shipping_amount
            if p.quantity == 0:
                messages.warning(request, "Please select item quantity !!")
                return redirect('/cart')
    else:
        return render(request, 'app/emptycart.html')

    return render(request, 'app/checkout.html', {'add': add, 'totalamount': total_amount, 'cart': cart})


@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('orders')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulations!! Profile Updated Successfully')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})


def delete_address(request, pk):
    address = Customer.objects.get(pk=pk)
    address.delete()
    return redirect('/address/')

