"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import *
from product.views import esewa_success, esewa_failure, KhaltiInitView, khalti_return, khalti_verify
# only for debugging purposes

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name = "Home" ),
    path('about/', about, name = 'About'),

    path('products/', include('product.urls')),
    path('dashboard/',include('adminpage.urls')),

    path('auth/',include('users.urls')),

    # esewa success and failure 
    path('esewa/success/<int:order_id>/', esewa_success, name='esewa_success'),
    path('esewa/failure/', esewa_failure, name='esewa_failure'),

    path("khalti/<int:pk>/init/", KhaltiInitView.as_view(), name="khalti_init"),
    path("payments/khalti/return/", khalti_return, name="khalti_return"),
    path("khalti/verify/", khalti_verify, name="khalti_verify"),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)