from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.JSONWebTokenAuth.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('my_profile/', views.ProfileView.as_view()),
    
]
