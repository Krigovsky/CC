from django.urls import path
from . import views


app_name = "cocktail"

urlpatterns = [
    path("", views.index, name='index'),
    path("registraition/", views.registraition, name='registraition'),
    path("view/", views.view, name='view'),
    path("startGolf/", views.start_golf, name='start_golf' ),
    path("card/", views.golf_card, name='golf_card'),
    path("update_score/<int:id>/", views.update_score, name="update_score"),
    path("scoreCard/<int:id>/", views.score_card, name="score_card"),
    
]
