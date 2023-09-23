from django.urls import path, include
from . import views

urlpatterns = [
    path('lucky_draw/', views.GetorSetLuckyDraw.as_view(),name="lucky_draw"),
    

]