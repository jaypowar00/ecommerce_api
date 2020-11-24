from django.contrib import admin
from . import models
# Register your models here.


# class DetailsAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'password', 'phone')
#
#
# class AddressAdmin(admin.ModelAdmin):
#     list_display = ('type', 'area', 'city', 'pinCode', 'state', 'country')


admin.site.register(models.Product)
admin.site.register(models.ProductDetails)
