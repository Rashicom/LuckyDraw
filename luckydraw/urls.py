from django.urls import path, include
from . import views

urlpatterns = [
    path('lucky_draw/', views.GetorSetLuckyDraw.as_view(),name="lucky_draw"),
    path('get_contest/<str:luckydrawtype_id>/', views.GetContext.as_view(), name="get_contest"),
    path('add_participant/', views.AddParticipant.as_view(), name="add_participant")



]