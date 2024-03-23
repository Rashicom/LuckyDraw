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
    path('additional_billing/', views.AdditionalBillingReport.as_view(),name="additional_billing"),

    # pdf generatin end points
    path('winners_report_pdf/', views.WinnerAnnouncementPdf.as_view(), name="winners_report_pdf"),
    
    path('user_report_pdf/', views.UserReportPdf.as_view(), name="user_report_pdf"),
    path('result_filter_pdf/', views.ResultFilterPdf.as_view(),name="result_filter_pdf"),
    path('additional_billing_pdf/', views.AdditionalBillingPdf.as_view(),name="additional_billing_pdf"),
]
