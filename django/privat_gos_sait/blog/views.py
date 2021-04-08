from django.shortcuts import render
from django.views.generic import ListView, DetailView
from . models import Post
from markdownx.utils import markdownify

# Create your views here.

class BlogListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    paginate_by = 10

class BlogDetailView(DetailView):
    model = Post
    template_name = 'blog/post.html'


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BlogDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['object'].content=markdownify(context['object'].content)
        return context
