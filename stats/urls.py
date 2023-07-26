from django.urls import path
from stats import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home-page'),
    path('teams', views.TeamsView.as_view(), name='teams-page'),
    path('teams/<team_id>', views.TeamDetailsView.as_view(), name='team-details-page'),
    path('players', views.PlayersView.as_view(), name='players-page'),
    path('players/<player_id>', views.PlayerDetailsView.as_view(), name='player-details-page'),
    path('find/', views.SearchView.as_view(), name='search')
]
