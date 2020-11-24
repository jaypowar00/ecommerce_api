from django.http import HttpResponse
from .models import *


def home(request):
    prod = Product.objects.all()
    print("\nresult:\n")
    out = ""
    for p in prod:
        out += f" ({p}) "
        print(f"{p}\n")
    return HttpResponse(f'''
    <h1>Home Page</h1><br>
    Total products are {out}
    ''')
