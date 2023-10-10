from django.urls import path, include
from . import views

urlpatterns = [
    path('lucky_draw/', views.GetorSetLuckyDraw.as_view(),name="lucky_draw"),
    path('get_contest/<str:luckydrawtype_id>/', views.Context.as_view(), name="get_contest"),
    path('add_participant/', views.AddParticipant.as_view(), name="add_participant"),
    path('draw/', views.AnnounceWinner.as_view(),name="draw"),
    path('delete_participant/', views.DeleteParticipant.as_view(),name="delete_participant"),
    path('results/', views.Results.as_view(),name="results"),
    path('user_report/',views.UserReport.as_view(),name="user_report"),
    
]