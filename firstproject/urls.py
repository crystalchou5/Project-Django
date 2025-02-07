"""
URL configuration for firstproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from myapp import views 
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('',views.index),
    path('tea/<str:pageindex>/',views.tea),
    path('index/',views.index),
    path('detail/<int:id>/',views.detail),  
    path('addcart/<str:type>/',views.addcart),
    path('addcart/<str:type>/<int:id>/',views.addcart),
    path('cart/',views.cart),
    path('order/',views.order), 
    path('ok/',views.ok),
    path('mail/<str:indexfrom>/',views.mail),
    path('captcha/',include('captcha.urls')),
    path('sendmail/<str:indexfrom>/',views.sendmail),
    path('login/',views.login),
    path('register/',views.register),
    path('index2/',views.index2),
    path('tea2/<str:pageindex>/',views.tea2),
    path('logout/',views.logout),
    path('detail2/<int:id>/',views.detail2),
    path('addcart_m/<str:type>/',views.addcart_m),
    path('addcart_m/<str:type>/<int:id>/',views.addcart_m),
    path('cart2/',views.cart2),
    path('order2/',views.order2),
    path('ok2/',views.ok2),
    path('orderlogin/<str:indexfrom>/',views.orderlogin),
    path('checkorder/<int:serial_number>/<str:indexfrom>/',views.checkorder),
    path('check/',views.check),
    path('hotproduct/<str:indexfrom>/',views.hotproduct),
    path('aboutus/<str:indexfrom>/',views.aboutus),
    path('member/<str:indexfrom>/',views.member),
    path('reference/',views.reference),
    path('forget/',views.forget),
    path('changepw/',views.changepw),
    path('forget_captcha/',views.forget_captcha),
    path('seller_login/',views.seller_login),
    path('seller_manage/',views.seller_manage),
    path('seller_manage/<str:page>/',views.seller_manage),
    path('edit_product/<int:id>/',views.edit_product),
    path('edit_product/<int:id>/<str:type>/',views.edit_product),
    path('add_product/',views.add_product),
    path('manage_order/<int:id>/',views.manage_order),
    path('manage_order/<int:id>/<str:type>/',views.manage_order),
    ]
