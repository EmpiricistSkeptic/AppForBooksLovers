from django.urls import path
from . import views


urlpatterns = [
    path('profile/', views.ProfileView, name='profile'),


]