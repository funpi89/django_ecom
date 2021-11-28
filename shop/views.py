from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from shop.models import Product
from django.core.paginator import Paginator

# Create your views here.


def home(req):
    return HttpResponse('<h1>hello David</h1>')

def post_view(req):
    if req.method == 'POST':
        data = req.POST
        mytext = data.get('mytest')
    return render(req, template_name='shop/test-form.html')

def product_detail_view(req, id):
    obj = get_object_or_404(Product, id=id)
    # qs = Product.objects.filter(id=id)
    # if not qs.exists() and qs.count() != 1:
    #     raise Http404
    # else:
    #     obj = qs.first()
    context = {'object': obj}
    template = 'shop/product-detail.html'

    return render(req, template, context)

def product_list_view(req):
    data = req.GET
    per_page = 3
    products = Product.objects.order_by('-updated_at')
    paginator = Paginator(products, per_page=per_page)
    try:
        page = int(data.get('p')) if data.get('p') else None
    except:
        raise Http404
    if page:
        try:
            products = paginator.page(page)
        except:
            raise Http404
    else:
        products = paginator.page(1)
    context = {'products': products, 'page_range': paginator.page_range}
    template = 'shop/product-list.html'

    return render(req, template, context)