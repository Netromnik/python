from django.shortcuts import render ,redirect ,get_object_or_404,get_list_or_404
from markdownx.utils import markdownify
from .models import pattern_for
from django.http import HttpResponse
from django.views.generic import ListView
# Create your views here.

def my_view(request):
    # View code here...
    return redirect('/mag/')


def post_titile(request,cat,slug):
    # This code for old base via categoy model
    # obj=get_object_or_404(pattern_for,categoy=cat,slug=slug,)
    # posts = pattern_for.objects.get(slug=slug,categoy=obj)

    posts= get_object_or_404(pattern_for, categoy=cat, slug=slug )
    posts.text=markdownify(posts.text)
    return render(request, 'pattern_for/post.html', {'posts': posts,'cat':cat})

def post_list(request,reder):
    # This code for old base via categoy model
    # obj=get_object_or_404(pattern_for,categoy=reder)
    # posts = pattern_for.objects.filter(categoy =reder)
    posts = get_list_or_404(pattern_for,categoy =reder)
    print(posts)
    return render(request,'pattern_for/index.html',context={'name':request,'post':posts})

