from django.urls import path
from . import views

urlpatterns = [
    # category URLs
    path('category/add/',views.add_category, name="add_category"),
    path('category/list/',views.categories, name="dashboard_categories"),
    path('category/update/<int:category_id>/',views.update_category, name="update_category"),
    path('category/delete/<int:category_id>/',views.delete_category, name="delete_category"),
    # product URLs
    path('product/add/',views.add_product, name="add_product"),
    path('product/list/',views.products, name="dashboard_products"),
    path('product/update/<int:product_id>/',views.update_product, name="update_product"),
    path('product/delete/<int:product_id>/',views.delete_product, name="delete_product"),
]