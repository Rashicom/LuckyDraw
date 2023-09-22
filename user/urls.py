from django.urls import path, include
from . import views


urlpatterns = [
    path('login/', views.UserLogin.as_view(), name="login"),
    path('logout/', views.UserLogout.as_view(), name="logout"),


]

