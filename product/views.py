from django.shortcuts import render, redirect

from ecommerce import settings
from .models import Product, Cart, Order, OrderItem
from django.contrib.auth.decorators import login_required 
from django.contrib import messages

from .forms import OrderForm

# for esewa payment integration to generate the signature.
import hmac
import hashlib
import base64
import uuid

from django.shortcuts import get_object_or_404
import json
import requests


from decimal import Decimal
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

# Create your views here.
def products(request):
    product_lists = Product.objects.all().order_by('-id')[:8]
    items = {
        'products': product_lists
    }
    return render(request, 'product/product_lists.html', items)

def product_details(request, product_id):
    product = Product.objects.get(id = product_id)
    items = {
        'product': product
    }
    return render(request, 'product/product_details.html', items)

# cart list
@login_required(login_url='/auth/login')
def cart_lists(request):
    user_carts= Cart.objects.filter(user= request.user)

    # setting total field in cart model
    for item in user_carts:
        item.total =item.product.product_price * item.quantity
  


    # sum of all cart total price
    subtotal = sum(item.total for item in user_carts)

    return render(request,'cart/cart.html',{'cart_items':user_carts, 'subtotal':subtotal})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity_str = request.POST.get('quantity', '1')
    quantity = int(quantity_str) if quantity_str.isdigit() and int(quantity_str) > 0 else 1

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"{product.product_name} added to cart successfully")
    return redirect("cart_lists")


# delete from cart
def delete_from_cart(request, cart_id):
    cart_item =Cart.objects.get(id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request,'cart item deleted successfully')
    return redirect('cart_lists') 

# hmac signature 
def generate_signature(key, message):
    key = key.encode('utf-8')
    message = message.encode('utf-8')
 
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()
 
    #Convert the digest to a Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')
 
    return signature


# esewa success
def esewa_success(request, order_id):
    context = {}
    order = get_object_or_404(Order, id=order_id)
    # order = Order.objects.get(id=order_id)

    # Get eSewa data from GET parameter
    data = request.GET.get('data')
    if data:
        decoded_data = base64.b64decode(data).decode('utf-8')
        data_dict = json.loads(decoded_data)
        status = data_dict.get('status')

        if status.upper() == 'COMPLETE':
            order.payment_status = 'completed'
            order.save()
            context['message'] = 'Payment successful. Order completed.'
        else:
            context['message'] = f'Transaction status: {status}'
    else:
        context['message'] = 'No payment data received.'

    return render(request, 'esewa/esewa_success.html', context)

def esewa_failure(request):
    return render(request, 'esewa/esewa_failure.html')


# KHALTI utils
def khalti_base_url() -> str:
    return "https://dev.khalti.com" if settings.KHALTI_IS_SANDBOX else "https://khalti.com"

def khalti_headers():
    return {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

def khalti_initiate(payload: dict) -> dict:
    url = f"{khalti_base_url()}/api/v2/epayment/initiate/"
    r = requests.post(url, headers=khalti_headers(), data=json.dumps(payload), timeout=20)
    return r.json()

def khalti_lookup(pidx: str) -> dict:
    url = f"{khalti_base_url()}/api/v2/epayment/lookup/"
    r = requests.post(url, headers=khalti_headers(), data=json.dumps({"pidx": pidx}), timeout=20)
    return r.json()

# Khalti views
class KhaltiInitView(View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, payment_status="Pending")

        payload = {
            "return_url": settings.KHALTI_RETURN_URL,
            "website_url": settings.KHALTI_WEBSITE_URL,
            "amount": int(Decimal(order.total_price) * 100),  # in paisa
            "purchase_order_id": str(order.pk),
            "purchase_order_name": f"Order-{order.pk}",
            "customer_info": {
                "name":  "CustomerName",
                "email": getattr(request.user, "email", "") or "customer@example.com",
                "phone": "9800000000",
            },
        }

        res = khalti_initiate(payload)
        pidx = res.get("pidx")
        payment_url = res.get("payment_url")

        if not pidx or not payment_url:
            return HttpResponseBadRequest(f"Khalti initiate failed: {res}")

        order.gateway = "khalti"
        order.gateway_ref = pidx
        order.save(update_fields=["gateway", "gateway_ref"])

        context = {
            "order": order,
            "pidx": pidx,
            "payment_url": payment_url,
            "amount": int(Decimal(order.total_price) * 100),
            "total_price": order.total_price,
            "return_url": settings.KHALTI_RETURN_URL,
            "website_url": settings.KHALTI_WEBSITE_URL,
        }
        return render(request, "khalti/khalti_form.html", context)


@csrf_exempt
def khalti_return(request):
    """ After payment Khalti redirects here with ?pidx=... """
    pidx = request.GET.get("pidx") or request.POST.get("pidx")
    if not pidx:
        return HttpResponseBadRequest("Missing pidx")

    order = get_object_or_404(Order, gateway="khalti", gateway_ref=pidx)
    data = khalti_lookup(pidx)
    status = str(data.get("status", "")).upper()

    if status in {"COMPLETED", "PAID", "SUCCESS"}:
        order.payment_status = "completed"
        order.save(update_fields=["payment_status"])
    else:
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])

    return redirect("order_lists")


@csrf_exempt
def khalti_verify(request):
    if request.method == "POST":
        pidx = request.POST.get("pidx")
        if not pidx:
            return JsonResponse({"error": "Missing pidx"}, status=400)

        # Call Khalti lookup
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
        }
        response = requests.post(
            "https://a.khalti.com/api/v2/epayment/lookup/",
            json={"pidx": pidx},
            headers=headers,
        )
        data = response.json()

        if data.get("status") == "Completed":
            # ✅ Mark order as paid
            order = Order.objects.get(gateway_ref=pidx)
            order.is_paid = True
            order.save()
            return redirect("order_summary", pk=order.pk)

        return JsonResponse(data, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

#  create order
def create_order(request):
    user_cart = Cart.objects.filter(user= request.user)
    total_price = sum(item.product.product_price * item.quantity for item in user_cart)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit = False)
            order.user = request.user
            order.total_price = total_price 
            order.save()

            for item in user_cart:
                order.items.create(
                    product = item.product,
                    quantity = item.quantity,
                    price = item.product.product_price * item.quantity
                ) # "items" is related name in orderitem.
                if order.payment_method == 'Cash on Delivery':
                    order.payment_status = 'Pending'
                    order.save()
                elif order.payment_method == 'Esewa':
                    transaction_uuid = uuid.uuid4()
                    tax_amount = 10  
                    total_amount = order.total_price + tax_amount
                    secret_key = '8gBm/:&EnhH.1/q'
                    data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code=EPAYTEST"
                    result = generate_signature(secret_key, data_to_sign)
                    context = {
                        'order': order,
                        'tax_amount':tax_amount,
                        'total_amount': total_amount,
                        'transaction_uuid': transaction_uuid,
                        'product_delivery_charge': 0,
                        'product_service_charge': 0,
                        'signature': result,
                        }
                    return render(request, 'esewa/esewa_form.html', context)


                elif order.payment_method == 'Khalti':
                    return redirect('khalti_init', pk=order.pk)
                
                user_cart.delete()
                return redirect('order_lists')
    else:
        form = OrderForm()
    return render(request, "order/order_form.html ", {'form': form})


# order list
def order_lists(request):
    orders = Order.objects.filter(user = request.user).order_by('created_date')
    return render(request, 'order/order_list.html', {'orders':orders})