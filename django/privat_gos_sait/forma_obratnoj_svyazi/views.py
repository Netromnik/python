from django.shortcuts import render,get_object_or_404
from markdownx.utils import markdownify
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .form import *
from .models import Contact_bd
from cart.cart import Cart
from pattern_for.models import pattern_for
# Create your views here.
def split_f(sp):
    l=list(sp)
    lr=''
    for i in l:
        lr=lr+" \n"+i
    return lr

def test(request,test):
    return HttpResponse(print(request.session))

def contact(request):

    if request.GET.get("name"):
        name=request.GET.get("name")
        cat=request.GET.get("cat")
        a=messange=get_object_or_404(pattern_for,slug=name,categoy=cat)
    else:
        a=""
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print ("tests")
            cart = Cart(request)
            l = [s['product'].name for s in cart]
            a=split_f(l)

            if request.GET.get("name"):
                a=a+"\n"+str(messange)
            cd =  form.cleaned_data
            Contact_bd.objects.create(name=cd['name'],
                    email = cd['email'],
                    phone = cd['phone'],
                    text  = cd['text'],
                    select_list = a 
                    )    
            cart.clear()
            return render(request,'form/post.html',context={'name':request,'usl':a})
    

    form=ContactForm()
    return render(request,'form/index.html',context={'name':request,'form':form,'cat':a})
