from django import forms


class sampleform(forms.Form):

    name = forms.CharField(required=True)
    age = forms.IntegerField(required=True)