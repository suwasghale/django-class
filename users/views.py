from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control

from .auth import redirect_if_logged_in

# Create your views here.
@redirect_if_logged_in
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully')
            return redirect('login_view')
        else:
            messages.error(request, 'Something went wrong')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@redirect_if_logged_in
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                messages.success(request, 'Login successful')
                if user.is_staff:
                    return redirect('dashboard_products')
                else:
                    next_url = request.GET.get('next', 'cart_lists')
                    return redirect(next_url)     
            else:

                messages.error(request, 'Login failed. Check your credentials.')

        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login_view')