from django.shortcuts import render
from django.views.generic.list import ListView
from pattern_for.models import pattern_for as prod_list
# Create your views here.
from django.shortcuts import get_object_or_404
from .models import items_cat, name_cat

class ArticleListView(ListView):
    model = items_cat
    queryset = posts = prod_list.objects.filter(categoy ='for_you')
    paginate_by = 6  # if pagination is desired
    template_name = 'product_category/mark.html'
#    queryset =items_cat.objects.filter()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


    def get_queryset(self):
        a=name_cat.objects.get(slug=self.kwargs['slug'])
        return items_cat.objects.filter(categoy=a.name)


def post_list(request):
    posts = name_cat.objects.all()
    return render(request, 'product_category/index.html', context={'name': request, 'post': posts})

def article(request,slug,cat):
    posts = items_cat.objects.get(slug=slug)
    print(posts)
    return render(request, 'product_category/post.html', context={'name': request, 'post': posts})
