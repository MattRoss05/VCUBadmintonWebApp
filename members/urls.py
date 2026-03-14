from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
  #url patterns for the authentication app
  path('logout_user/', views.logout_user, name = 'logout'),
  path('join/', views.register_user, name = 'join'),

]