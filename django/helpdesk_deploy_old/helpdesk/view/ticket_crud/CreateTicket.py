from django import forms
from django.shortcuts import resolve_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormView
from upload_validator import FileTypeValidator

from base.models import Task, Queue, Stream
from mixin.generic_viev.page import Page, BreadcrumbItem


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
        self.fields['stream'].choices = self.categories_as_choices()
        print(type(self.fields['stream']))

    # files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    files = forms.FileField(
    label='Загрузка файлов', help_text="Разрешенные форматы: JPEG/jpg , PNG, zip, pdf,txt,doc/docx", required=False,
    validators=[CustomFileTypeValidator(
        allowed_types=[ 'application/msword','image/jpeg','image/jpg','image/png','application/zip','application/pdf','text/plain'],
        allowed_extensions=['.zip', '.txt','.jpeg' ,'.png', '.pdf','.jpg','.doc', '.docx']
    )]
)

    def categories_as_choices(self):
        categories = []
        for category in Queue.obj.all():
            new_category = []
            sub_categories = []
            for sub_category in Stream.obj.filter(queue=category,in_public=True):
                sub_categories.append([sub_category.id, sub_category.description])
            new_category = [category.name, sub_categories]
            categories.append(new_category)

        return categories

    class Meta:
        model = Task
        fields = ['title', 'description', 'stream', 'date_due']
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'stream': 'Тема',
            "date_due" : "Время окончания"
        }
        widgets = {
        'date_due': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
    }


class ContactView(FormView,Page):
    template_name = "locations/ticket_crud/create/ticket_create.html"
    template_name_sucefful = "locations/ticket_crud/thanks.html"
    form_class = TicketForm
    success_url = '?thanks=ok'
    pk = None
    breadcrumb_list =[ BreadcrumbItem(name="Дашборд",is_active=False,url="/") ,BreadcrumbItem(name="Создания заявки",is_active=True,url="/wiki/"),]
    title = "Создания заявки"
    # def get(self, request, *args, **kwargs):
    #     # if request.GET.get("thanks"):
    #     #     return render(request,self.template_name_sucefful)
    #     return  super().get(request, args, kwargs)

    def get_success_url(self):
        return resolve_url("view:detail_ticket",pk=self.pk)

    def form_valid(self, form):
        if form.is_valid():
            data = form.cleaned_data
            t = Task()
            t.title = data['title']
            t.description = data['description']
            t.stream = data['stream']
            t.date_due = data['date_due']
            t.autors = self.request.user
            t.chenge_user = self.request.user
            t.status = t.STATUS[0][0]
            t.save()
            file =self.request.FILES.get('files')
            if file != None:
                t.upload_file(file)
            self.pk= t.pk
        return super(ContactView, self).form_valid(form)

