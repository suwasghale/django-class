from django.shortcuts import redirect, render
from django.contrib import messages
from users.auth import admin_only 
from django.contrib.auth.decorators import login_required
# from django.urls import reverse_lazy

from product.forms import CategoryForm, ProductForm
from product.models import Product, Category
# Create your views here.
@admin_only
@login_required(login_url='login_view')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dashboard/category/list')

    else:
        form = CategoryForm()        

    return render(request,'add_category.html',{'form':form})

# getting categories
@admin_only
@login_required(login_url='login_view')
def categories(request):
    categories = Category.objects.all().order_by('-created_date')
    return render(request, 'categories.html', {'categories': categories})

# update category
@admin_only
@login_required(login_url='login_view')
def update_category(request, category_id):
    instance = Category.objects.get(id = category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "category updated successfully." )
            return redirect('dashboard_categories')
        else:
            messages.error(request, "Error on updating category.")
    else:
        form = CategoryForm(instance = instance)
    return render(request, 'update_category.html', {'form':form})

# delete category
@admin_only
@login_required(login_url='login_view')
def delete_category(request, category_id):
    category = Category.objects.get(id = category_id)
    category.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect('dashboard_categories')

@admin_only
@login_required(login_url='login_view')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard_products')

    else:
        form = ProductForm()        

    return render(request,'add_product.html',{'form':form})


# getting products
@admin_only
@login_required(login_url='login_view')
def products(request):
    products = Product.objects.all().order_by('-created_date')
    return render(request, 'products.html', {'products': products})


# update product
@admin_only
@login_required(login_url='login_view')
def update_product(request, product_id):
    instance = Product.objects.get(id = product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully." )
            return redirect('dashboard_products')
        else:
            messages.error(request, "Error on updating product.")
    else:
        form = ProductForm(instance = instance)
    return render(request, 'update_product.html', {'form':form})

# delete product
@admin_only
@login_required(login_url='login_view')
def delete_product(request, product_id):
    product = Product.objects.get(id = product_id)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('dashboard_products')
