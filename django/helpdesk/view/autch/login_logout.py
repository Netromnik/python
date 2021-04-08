from django.shortcuts import redirect
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import reverse
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url


class LowerUsernameField(UsernameField):
    def to_python(self, date):
        return super().to_python(date.lower())


class LoginForm(AuthenticationForm):
    username = LowerUsernameField(widget=forms.TextInput(attrs={'autofocus': True, }), label="Логин")

    password = forms.CharField(
        label=("Пароль"),
        strip=False,
        widget=forms.PasswordInput,
    )

class Login(LoginView):
    template_name = "login/login.html"
    redirect_authenticated_user = True
    form_class = LoginForm

    # metods  return  url redirection
    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse("admin:index")
        else:
            return reverse("view:dasbord")


class Logout(LogoutView):
    template_name = "registration/logged_out.html"
