from django.urls import path
from . import views


app_name = "cocktail"

urlpatterns = [
    path("", views.index, name='index'),
    path("registraition/", views.registraition, name='registraition'),
    path("view/", views.view, name='view'),
    path("startGolf/", views.start_golf, name='start_golf' ),
    path("card/", views.golf_card, name='golf_card'),
    path("update_score/<int:id>/<int:hole>", views.update_score, name="update_score"),
    path("scoreCard/<int:id>/<hole>", views.score_card, name="score_card"),
    path("change_hole/<int:id>/<int:hole>/", views.go_to_n_hole, name="hole")
]
