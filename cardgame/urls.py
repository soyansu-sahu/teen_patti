from django.urls import path
from .views import play_game, bet, user_signup, user_login, user_logout,home,switch_turn,showdown,see_action,raise_action,fold_action,showdown

urlpatterns = [
    path('', home, name='home'),
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('play/', play_game, name='play_game'),
    path('bet/<int:game_id>/', bet, name='bet'),
    path('switch_turn/<int:game_id>/',switch_turn, name='switch_turn'),
    path('showdown/<int:game_id>/',showdown, name='showdown'),
    path('see_action/',see_action, name='see_action'),
    path('raise_action/<int:game_id>/', raise_action, name='raise_action'),
    path('fold_action/',fold_action, name='fold_action'),
    path('showdown_action/',showdown, name='showdown_action'),
    

]
