from django import forms


# login form
class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.Field(required=True)



class CreateUserForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.Field(required=True)