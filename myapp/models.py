from django.db import models


# Create your models here.

class ProductModel(models.Model):
    pname = models.CharField(max_length=100,blank=True,default='')
    pimage = models.CharField(max_length=200,blank=True,default='')
    pprice = models.IntegerField(default=0)
    member_price = models.IntegerField(default=0)
    pdescription = models.TextField(blank=True,default='')
    hot = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.pname
    
class OrderModel(models.Model):
    total = models.IntegerField(default=0)
    shipping = models.IntegerField(default=0)
    grandtotal = models.IntegerField(default=0)
    customname = models.CharField(max_length=50,null=False,default='')
    customphone = models.CharField(max_length=50,null=False,default='')
    customaddress = models.CharField(max_length=100,null=False,default='')
    customemail = models.EmailField(null=False,default='')
    paytype = models.CharField(max_length=50,default='')

    def __str__(self):
        return self.customname

class DetailModel(models.Model):
    dorder = models.ForeignKey('OrderModel',on_delete=models.CASCADE)
    pname = models.CharField(max_length=100,blank=True,default='')
    pimage = models.CharField(max_length=200,blank=True,default='')
    unitprice = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    total = models.IntegerField(default=0)

    def __str__(self):
        return self.pname

