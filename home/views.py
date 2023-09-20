from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from . import forms

# Create your views here.

class test(View):

    def get(self, request, *args, **kwargs):
        return render(request, "test.html")

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        age = request.POST.get("age")
        print(name)
        print(age)

        form = forms.sampleform(request.POST)
        if form.is_valid():
            return HttpResponse("OK")
        else:
            return HttpResponse("NOT VALIED")

        
