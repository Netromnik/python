from django.views.generic import View
from mixin.generic_viev.page import Page,BreadcrumbItem
from django import forms
from .models import WikiArticleModel
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.http import HttpResponse

def wiki_dasbord(request,**kwargs):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    else:
        node_tree = WikiArticleModel.node_manager.get_node_root()
        node_tree.append(WikiArticleModel.node_manager.get_not_publisk_node(request.user))
        contex = {
            "node_tree":node_tree
        }
        return render(request, 'locations/wiki_dasbord.html',contex)

class PublishForm(forms.Form):
    def __init__(self, *args, **kwargs):
        wp_p = kwargs["wp"].is_publish
        del kwargs["wp"]
        super(PublishForm, self).__init__(*args, **kwargs)

    state = forms.CharField(widget=forms.HiddenInput())

class WikiPage(Page,View):
    title = "Вики"
    menu_item = []
    breadcrumb_list = []
    breadcrumb_list_dir =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="вики",is_active=True,url="/wiki/"),]
    template_name = "locations/wiki_page.html"
    manager = WikiArticleModel.node_manager

    def get_context_data(self, **kwargs):
        obj_pk = kwargs.get("pk")
        self.breadcrumb_list = []
        self.breadcrumb_list = self.ext_get_breadcrumb(obj_pk)
        kwargs = super(WikiPage, self).get_context_data(**kwargs)
        node_tree = self.manager.get_node_root()
        node_tree.append(self.manager.get_not_publisk_node(self.request.user))
        kwargs["node_tree"]     = node_tree
        kwargs["active_node"]   = self.manager.get_node_content(obj_pk)
        kwargs["readOnly"]   = "true"
        kwargs["is_edit"]   =  self.manager.get_write(self.request.user,obj_pk)
        return  kwargs

    def ext_get_breadcrumb(self,pk):
        obj = self.manager.get(pk= pk)
        breadcrumb_list = self.breadcrumb_list_dir +[ BreadcrumbItem(name=i["title"],is_active=True,url=i["url"]) for i in self.manager.get_materilize(pk)]
        breadcrumb_list.append(BreadcrumbItem(name=obj.title,is_active=False,url=obj.url()))
        return breadcrumb_list

class WikiPageEdit(Page,View):
    title = "Вики"
    menu_item = []
    breadcrumb_list = []
    breadcrumb_list_dir =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="вики",is_active=True,url="/wiki/"),]
    template_name = "locations/wiki_page.html"
    manager = WikiArticleModel.node_manager
    def get_context_data(self, **kwargs):
        kwargs = super(WikiPageEdit, self).get_context_data(**kwargs)
        pk = kwargs["pk"]
        wn = self.manager.get(pk=pk)
        self.breadcrumb_list =[]
        self.breadcrumb_list = self.ext_get_breadcrumb(pk)
        node_tree = self.manager.get_node_root()
        node_tree.append(self.manager.get_not_publisk_node(self.request.user))
        kwargs["node_tree"]     = node_tree
        kwargs["active_node"]   = wn
        kwargs["is_publish"]   = wn.is_publish
        kwargs["form"]   = PublishForm(wp=wn)
        kwargs["readOnly"]   = "false"
        return  kwargs

    def post(self, request, *args, **kwargs):
        wp = self.manager.get(pk=kwargs["pk"])
        if request.is_ajax():
            # save content use editorjs
            wp.content = request.body.decode("utf-8")
            wp.change_user = request.user
            wp.save()
            return HttpResponse("200")

        form = PublishForm(request.POST,wp=wp)
        # check whether it's valid:
        if form.is_valid():
            data = form.cleaned_data['state']
            wp.is_publish = data
            wp.save()
        return self.get(self, request, *args, **kwargs)

    def ext_get_breadcrumb(self,pk):
        obj = self.manager.get(pk= pk)
        breadcrumb_list = self.breadcrumb_list_dir +[ BreadcrumbItem(name=i["title"],is_active=True,url=i["url"]) for i in self.manager.get_materilize(pk)]
        breadcrumb_list.append(BreadcrumbItem(name=obj.title,is_active=False,url=obj.url()))
        return breadcrumb_list
