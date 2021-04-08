from django.views.generic import TemplateView
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin

class BreadcrumbItem:
    is_active = False
    name = "None"
    url = "#"
    def __init__(self,name,is_active,url):
        self.name=name
        self.is_active=is_active
        self.url=url

class Page(TemplateView):
    title = "No"
    breadcrumb_list = None
    menu_item = []
    def get_context_data(self, **kwargs):
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
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return self.breadcrumb_list
