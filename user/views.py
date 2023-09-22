from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout


# Login
class UserLogin(View):

    form_class = LoginForm
    login_templet = "login.html"
    home_templet = "home.html"

    def post(self, request, *args, **kwargs):
        """
        accept: email, password
        this method validating login credencials using
        login form, then authenticate user
        """
        
        # creting form using data
        login_form = self.form_class(request.POST)
        print(request.POST.get('email'))
        print(type(request.POST.get('email')))
        # validating form
        # if the form is not valied return error response
        if not login_form.is_valid():
            print("emial not valied")
            return render(request, self.login_templet, {'error': "Pleace provide a valied email and password"})
        print("valied")
        
        # if the form is valied procide for authentication and login
        # fetch cleaned data to authenticate
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password'].strip()

        # authentication
        user = authenticate(request, email=email, password=password)
        if user is not None:
            """
            AUTHENTICATED
            login() creates session and return cookies
            for authenticated user
            """
            login(request,user)

            # provide home templet, message optional
            templet = self.home_templet
            message = {}
        
        else:
            """
            AUTHENTICATION FAILED
            """

            # render the same page with error response
            templet = self.login_templet
            message = {"error":"invalied email or password"}

        # return
        return render(request, templet, message)
        

    def get(self, request, *args, **kwargs):
        """
        returning login template
        """
        return render(request, self.login_templet)
        



class UserLogout(View):

    def get(self, request, *args, **kwargs):
        """
        clearing sessions and loging out
        """

        # logout and redirect to login page
        logout(request)
        return redirect('login')

