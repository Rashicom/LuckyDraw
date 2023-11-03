from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import forms
from user.models import CustomUser

# Create your views here.

class AdminLogin(View):

    templet = "Admin_login.html"
    form_class = forms.LoginForm

    def post(self, request):
        """
        accept: email, password
        this method validating login credencials using
        login form, then authenticate user
        """
        
        # creting form using data
        login_form = self.form_class(request.POST)

        # validating form
        # if the form is not valied return error response
        if not login_form.is_valid():
            print("not valied")
            return render(request, self.login_templet, {'error': "Pleace provide a valied email and password"})
        
        # if the form is valied procide for authentication and login
        # fetch cleaned data to authenticate
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password'].strip()

        # authentication
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_superuser:
            """
            AUTHENTICATED
            login() creates session and return cookies
            for authenticated user
            """
            login(request,user)
            return redirect("manage_user")
        
        else: 
            """
            AUTHENTICATION FAILED
            """
            # render the same page with error response
            message = {"error":"invalied email or password"}
            
            # return
            return render(request, self.templet, message)
        

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("manage_user")

        return render(request,self.templet)

    


class ManageUser(View):

    templet = "Admin_usermanage.html"

    @method_decorator(login_required(login_url="admin_login"))
    def get(self, request):
        """
        this view is returning admin user management page
        """
        user = request.user

        # restrict non admin users from accessing the views
        if not user.is_superuser:
            return redirect("admin_login")
        
        user_list = CustomUser.objects.all().exclude(is_superuser=True)

        return render(request,self.templet,{"user_list":user_list})


class AdminLogout(View):

    def get(self, request):
        """
        clearing sessions and loging out
        """

        # logout and redirect to login page
        logout(request)
        return redirect('admin_login')
