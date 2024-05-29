from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Users
from django import forms


class SignUpForm(UserCreationForm):

    class Meta:
        model = Users
        fields = ["email"]
        labels = {"email": "メールアドレス"}

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["placeholder"] = ""


class LoginForm(AuthenticationForm):
    # username = forms.CharField(label="メールアドレス")

    class Meta:
        model = Users

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["placeholder"] = ""
