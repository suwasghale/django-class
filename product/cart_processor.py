from .models import Cart



def cart_items(request):
    if request.user.is_authenticated:   
        user_carts =Cart.objects.filter(user =request.user)
        cart_count = sum(cart.quantity for cart in user_carts)
    else:
        cart_count =0

    return{
        'cart_count': cart_count
    }