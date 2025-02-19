from django.urls import path
from . import views


app_name = "cocktail"

urlpatterns = [
    #basics
    path("", views.index, name='index'),
    path("view/", views.view, name='view'),

    #Registrations of team/admin
    path("registraition/", views.registraition, name='registraition'),
    path("teams/", views.teams, name="teams"),
    path("login/", views.login, name="login"),

    #golfing portion
    path("startGolf/", views.start_golf, name='start_golf' ),
    path("card/", views.golf_card, name='golf_card'),
    path("update_score/<int:id>/<int:hole>", views.update_score, name="update_score"),
    path("scoreCard/<int:id>/<hole>", views.score_card, name="score_card"),
    path("change_hole/<int:id>/<int:hole>/", views.go_to_n_hole, name="hole"),

    #cocktail portion
    path("cocktail_start/", views.start_cocktail, name="cocktail_start"),
]
