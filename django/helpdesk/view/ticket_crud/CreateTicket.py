from django.core.exceptions import ImproperlyConfigured
from django.views.generic.edit import FormView
from django import forms
from fsm.models import Task,Queue
from mixin.generic_viev.page import  BreadcrumbItem
from upload_validator import FileTypeValidator
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeNodeChoiceField

class CustomFileTypeValidator(FileTypeValidator):
    type_message = _(
        "Фаел типа '%(detected_type)s' не допускается. "
        "Допустимые типы: '%(allowed_types)s'."
    )

    extension_message = _(
        "Расширение файла '%(extension)s' не допускается. "
        "Допустимые расширения: '%(allowed_extensions)s'."
    )

    invalid_message = _(
        "Допустимый тип '%(allowed_type)s' не допустимый тип. "
    )

# ModelChoiceField.choices
class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.get("user")
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = self.categories_as_choices()
        self.fields['category'].label = "Выберите отдел для отправки"

    # files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    category = TreeNodeChoiceField(queryset=Queue.objects.all())

    files = forms.FileField(
    label='Загрузка файлов', help_text="Разрешенные форматы: JPEG/jpg , PNG, zip, pdf,txt,doc/docx", required=False,
    validators=[CustomFileTypeValidator(
        allowed_types=[ 'application/msword','image/jpeg','image/jpg','image/png','application/zip','application/pdf','text/plain'],
        allowed_extensions=['.zip', '.txt','.jpeg' ,'.png', '.pdf','.jpg','.doc', '.docx']
    )]
)

    def categories_as_choices(self):
        categories = []
        for category in Queue.objects.filter(parent=None):
            new_category = []
            sub_categories = []
            for sub_category in category.get_children():
                sub_categories.append([sub_category.id, sub_category.title])
            new_category = [category.title, sub_categories]
            categories.append(new_category)
        return categories
    def clean_category(self):
        return self.cleaned_data['category'].get_root()



    class Meta:
        model = Task
        fields = ['title', 'description', 'the_importance']
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'the_importance':"Важность",
        }
    #     widgets = {
    #     'date_due': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
    # }


class ContactView(FormView):
    template_name = "locations/ticket_crud/create/ticket_create.html"
    form_class = TicketForm
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Создания заявки",is_active=True,url="/wiki/"),]
    title = "Создания заявки"
    def get_context_data(self, **kwargs):
        kwargs = super(ContactView, self).get_context_data(**kwargs)
        kwargs["breadcrumb_list"] = self.get_breadcrumb()
        kwargs["title"] = self.title
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

    def form_valid(self, form):
        if form.is_valid():
            data = form.cleaned_data
            t = Task()
            t.title = data['title']
            t.description = data['description']
            t.queue = data['category']
            t.the_importance = data['the_importance']
            t.owner = self.request.user
            t.save()
            file =self.request.FILES.get('files')
            if file != None:
                t.upload_file(file)
            t.start()
            self.success_url = t.url()
        return super(ContactView, self).form_valid(form)
