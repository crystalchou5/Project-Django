from django.contrib import admin
from .models import ProductModel,OrderModel,DetailModel
 
# Register your models here.
admin.site.register(ProductModel)
admin.site.register(OrderModel)
admin.site.register(DetailModel)
