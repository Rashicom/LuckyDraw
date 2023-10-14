from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from luckydraw.models import LuckyDraw,Participants

# Login
class UserLogin(View):

    form_class = LoginForm
    login_templet = "lucky_login.html"
    home_templet = "lucky_index.html"

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
            print("not valied")
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

            # calculating total sales profit
            coupen_price = 0
            prize_given = 0
            for i in Participants.objects.filter(context_id__is_winner_announced=True):
                coupen_price += i.coupen_rate
                
                if i.is_winner:
                    prize_given += i.prize_rate * i.coupen_count
            
            profit = coupen_price - prize_given


            # return
            templet = self.home_templet
            luckydrow_list = LuckyDraw.objects.all()
            return render(request,templet,{"luckydrow_list":luckydrow_list,"profit":profit})
        
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
        if request.user.is_authenticated:

            # calculating total sales profit
            coupen_price = 0
            prize_given = 0
            for i in Participants.objects.filter(context_id__is_winner_announced=True):
                coupen_price += i.coupen_rate
                
                if i.is_winner:
                    prize_given += i.prize_rate * i.coupen_count
            
            profit = coupen_price - prize_given

            luckydrow_list = LuckyDraw.objects.all()
            return render(request,self.home_templet,{"luckydrow_list":luckydrow_list,"profit":profit})

        return render(request, self.login_templet)
        

# logout user
class UserLogout(View):

    
    def get(self, request, *args, **kwargs):
        """
        clearing sessions and loging out
        """

        # logout and redirect to login page
        logout(request)
        return redirect('login')

