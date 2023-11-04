from django.urls import path, include
from . import views


urlpatterns = [
    path('login/', views.AdminLogin.as_view(), name="admin_login"),
    path('manage_user/', views.ManageUser.as_view(), name="manage_user"),
    path('admin_logout/', views.AdminLogout.as_view(), name="admin_logout"),
    path('kerala/', views.KeralaDear.as_view(), name="kerala"),
    path('dear1/', views.Dear1.as_view(), name="dear1"),
    path('dear2/', views.Dear2.as_view(), name="dear2"),
    path('dear3/', views.Dear3.as_view(), name="dear3"),
    path('extra/', views.Extra.as_view(), name="extra"),
    
    path('create_user/', views.CreateUser.as_view(), name="create_user"),
    path('delete_user/', views.DeleteUser.as_view(), name="delete_user")
    
    
]