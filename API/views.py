from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
import jwt, json
from user.decorators import *
from .models import *
from user.models import *
from .serializers import *
from user.serializers import *
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([AllowAny])
def products_view(request):
    prod = Product.objects.all()
    serialized_products = ProductSerializer(prod, many=True).data
    products = {'total_products': 0, 'products': dict()}
    totalProducts = len(serialized_products)
    for product in serialized_products:
        product = dict(product)
        products['products'][product['productId']] = product
    products['total_products'] = totalProducts
    return Response({'response': products, 'status': True})


@api_view(['GET'])
def fun(request):
    pass
