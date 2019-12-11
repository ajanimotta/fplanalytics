from django.urls import path
from . import views 

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('index.html', views.homepage, name='homepage'),
    path('teams.html', views.teams, name='teams'),
    path('gkps.html', views.gkps, name='gkps'),
    path('defs.html', views.defs, name='defs'),
    path('mids.html', views.mids, name='mids'),
    path('fwds.html', views.fwds, name='fwds'),
    path('elements.html', views.elements, name='elements'),
    path('players.html', views.players, name='players'),
]