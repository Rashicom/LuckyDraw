from django import forms
from .models import CustomUser


# login form
class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.Field(required=True)




