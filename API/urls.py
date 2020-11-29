from django.urls import path
from .views import *

urlpatterns = [
    path('products', products_view, name='home'),
    # path('products', products_view, name='home'),
]
