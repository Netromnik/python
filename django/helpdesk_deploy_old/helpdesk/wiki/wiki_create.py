from django.views.generic.edit import FormView ,UpdateView
from django import forms
from .models import WikiArticleModel , WikiPermModel
from mixin.generic_viev.page import Page, BreadcrumbItem
from django.utils.translation import ugettext_lazy as _

# ModelChoiceField.choices
class BaseWikiForm(forms.ModelForm):

    class Meta:
        model = WikiArticleModel
        fields = ["title","slug","order", ]
        labels = {
            'title': 'Заголовок',
            'slug': 'Чпу',
            'order': 'Порядок',
        }

class WikiForm(BaseWikiForm):
    dep = forms.ChoiceField(
                            widget=forms.Select,
                            label=_('Место расположения'), help_text=_("Можно вставить только в разрешенные вам места"),
                            required=False,
                            )

    def __init__(self, user, *args, **kwargs):
        super(WikiForm, self).__init__(*args, **kwargs)
        self.fields['dep'].choices = self.categories_as_choices(user)

    def categories_as_choices(self, user):
        cat = [ (i.node.pk,i.node.title) for i in WikiPermModel.manager_perm.filter(group__in=user.groups.all()) if i.node.level==0 ]

        return cat


class WikiNews(FormView,Page):
    template_name = "locations/wiki_create.html"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Создания записи",is_active=True,url="/wiki/"),]
    title = "Создания записи"
    form_class = WikiForm
    success_url = '?thanks=ok'
    pk = None

    def get_success_url(self):
        wn = WikiArticleModel.node_manager.get(pk=self.pk)
        return wn.url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            data = form.cleaned_data
            wn = WikiArticleModel()
            wn.title = data['title']
            wn.slug = data['slug']
            wn.is_publish = False
            wn.change_user = self.request.user
            wn.author = self.request.user
            wn.order = data['order']
            WikiArticleModel.node_manager.get(pk = data["dep"] ).add_children(wn)
            wn.save()
            self.pk= wn.pk
        return super().form_valid(form)

class WikiUpdate(UpdateView):
    template_name = "locations/wiki_create.html"
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Обновления записи",is_active=True,url="/wiki/"),]
    title = "Обновления записи"
    model = WikiArticleModel
    form_class = WikiForm
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        wn = self.model.node_manager.get(pk=self.pk)
        return wn.url()

    def get_object(self, queryset=None):
        return self.model.node_manager.get(pk = self.kwargs["pk"])

    def form_valid(self, form):
        data = form.cleaned_data
        wn = self.get_object()
        wn.title = data['title']
        wn.slug = data['slug']
        wn.change_user = self.request.user
        wn.order = data['order']
        WikiArticleModel.node_manager.get(pk=data["dep"]).add_children(wn)
        wn.save()
        self.pk= wn.pk
        return super(WikiUpdate, self).form_valid(form)
