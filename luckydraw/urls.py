from django.urls import path, include
from . import views

urlpatterns = [
    path('lucky_draw/', views.GetorSetLuckyDraw.as_view(),name="lucky_draw"),
    path('get_contest/<str:luckydrawtype_id>/', views.Context.as_view(), name="get_contest"),
    path('add_participant/', views.AddParticipant.as_view(), name="add_participant"),
    path('draw/', views.AnnounceWinner.as_view(),name="draw"),
    path('delete_participant/', views.DeleteParticipant.as_view(),name="delete_participant")

    
]




# server {
#     listen 80;
#     server_name 13.49.64.76;

#     location = /favicon.ico { access_log off; log_not_found off; }
#     location /static/ {
#         alias /home/ubuntu/LuckyDraw/static-cdn/;
#     }

#     location / {
#         include proxy_params;
#         proxy_pass http://unix:/run/gunicorn.sock;
#     }
# }