from django.urls import path, include
from . import views


urlpatterns = [
    path('test/', views.test.as_view()),
    

]