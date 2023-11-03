from django.urls import path, include
from . import views


urlpatterns = [
    path('login/', views.AdminLogin.as_view(), name="admin_login"),
    path('manage_user/', views.ManageUser.as_view(), name="manage_user"),
    path('admin_logout/', views.AdminLogout.as_view(), name="admin_logout"),
    
    
]