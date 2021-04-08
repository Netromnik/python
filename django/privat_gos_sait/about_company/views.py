from django.shortcuts import render
from django.shortcuts import get_object_or_404 ,redirect
from markdown import markdown
from .models import about_company,item_block,list_menu
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from blog.models import Post

def my_rederect(request):
    return redirect("/news/")
from itertools import chain
# Create your views here.
class My_list_views(ListView):
    model=list_menu
    template_name="about_company/index.html"


    def content_render(request):
        response = HttpResponse()
        items_block= item_block.objects.all()
        response.write(render(request,'about_company/block-img.html',context={'name':request,'block':items_block}).content)
        lists_menu= list_menu.objects.all()
        response.write(render(request,'about_company/glob_meny.html',context={'name':request,'list_menu':lists_menu}).content)

        return HttpResponse(render(request,'about_company/index.html',context={'post':str(response.content.decode('utf-8'))}).content)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test']=Post.objects.all()
        return context


def DetailView(request,slug):
    model=list_menu
    template_name="about_company/post.html"
    my_object = get_object_or_404(model, slug=slug)
    return render(request,template_name,context=({'post':my_object}))