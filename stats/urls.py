from django.urls import path
from stats import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home-page'),
    path('teams', views.TeamsView.as_view(), name='teams-page'),
    path('teams/<slug:slug>', views.TeamDetailsView.as_view(), name='team-details-page'),
    path('players', views.PlayersView.as_view(), name='players-page'),
    path('players/<slug:slug>', views.PlayerDetailsView.as_view(), name='player-details-page'),
    path('matches/<slug:slug>', views.MatchDetailsView.as_view(), name='match-details-page'),
    path('compare', views.ComparePlayersView.as_view(), name='compare-players'),
    path('find/', views.SearchView.as_view(), name='search'),
    path('spoilers/<slug:slug>', views.SeeSpoilersView.as_view(), name='see-spoilers'),
    path('toggle-mode/', views.ToggleModeView.as_view(), name='toggle-mode'),
]
