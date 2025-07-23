from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, include


app_name = "cocktail"

urlpatterns = [
    #basics
    path("", views.index, name='index'),
    path("view/", views.view, name='view'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    #Registrations of team/admin
    path("registraition/", views.registraition, name='registraition'),
    path("teams/", views.teams, name="teams"),
    path("login/", views.user_login, name="login"),
    path("register/", views.user_registraition, name="register"),
    path("user_display/<int:user_id>", views.user_display, name="user_display"),
    path("start/", views.start_competition, name="start"),
    path("user_management/<int:id>", views.user_management, name="user_management"),
    path("create_team/", views.create_team, name="create_team"),
    path("join_team/", views.join_team, name="join_team"),

    #golfing portion
    # path("startGolf/", views.start_golf, name='start_golf' ), #deprecated
    path("card/", views.golf_card, name='golf_card'),
    path("update_score/<int:id>/<int:hole>", views.update_score, name="update_score"),
    path("scoreCard/<int:id>/<hole>", views.score_card, name="score_card"),
    path("change_hole/<int:id>/<int:hole>/", views.go_to_n_hole, name="hole"),

    #cocktail portion
    path("cocktail/<int:id>", views.cocktail, name="cocktail"),
    path("cocktail_card/<int:id>", views.cocktail_card, name="cocktail_card"),
    path("cocktail_add/<int:id>", views.cocktail_add, name="cocktail_add"),
    path("cocktail_inbetween/<int:id>", views.cocktail_joining, name="cocktail_joining")

]
