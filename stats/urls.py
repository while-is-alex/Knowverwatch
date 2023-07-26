from django.urls import path
from stats import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home-page'),
    path('teams', views.TeamsView.as_view(), name='teams-page'),
    path('players', views.PlayersView.as_view(), name='players-page'),
    path('teams/<team_id>', views.TeamDetailsView.as_view(), name='team-details-page'),
    # path('players/<player>'),
]
