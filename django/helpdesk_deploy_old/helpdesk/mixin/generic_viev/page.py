from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView


class BreadcrumbItem:
    is_active = False
    name = "None"
    url = "#"
    def __init__(self,name,is_active,url):
        self.name=name
        self.is_active=is_active
        self.url=url

class Page(LoginRequiredMixin,TemplateView):
    title = "No"
    breadcrumb_list = None
    menu_item = []
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["breadcrumb_list"] = self.get_breadcrumb()
        kwargs["title"] = self.title
        kwargs["menu_item"] = self.menu_item
        return  kwargs

    def get_breadcrumb(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response() is overridden.
        """
        if self.breadcrumb_list is None:
            raise ImproperlyConfigured("define  breadcrumb_list")
        else:
            return self.breadcrumb_list
