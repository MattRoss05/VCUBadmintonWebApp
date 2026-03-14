from django.urls import path
from . import views


urlpatterns = [
    #associate url patterns with view functions in the home app and name them so they can be referenced in the html templates.
    path('', views.welcome_page, name = 'welcome'),
    path('about/', views.about_page, name = 'about'),
    path('rankings/', views.display_rank, name = 'rankings'),
    path('match/', views.match_page, name = 'match'),
    path('leave/', views.leave_ranks, name = 'leave'),
    path('matchconfirm/', views.display_message, name = 'message'),
    path('forbidden/', views.not_authenticated, name = 'forbidden'),
]
