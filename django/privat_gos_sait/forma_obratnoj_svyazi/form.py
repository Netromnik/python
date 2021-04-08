from django import forms

class ContactForm(forms.Form):
    name =forms.CharField(label='Имя',max_length=20)
    email =forms.EmailField(label='Email ')
    phone=forms.CharField(label='Телефон',max_length=11)
    text=forms.CharField(label='Сообщение ',max_length=200,widget=forms.Textarea)
    CHOICES = (('Option 1', 'Option 1'),('Option 2', 'Option 2'),)
