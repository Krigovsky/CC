from django.urls import path
from . import views


app_name = "cocktail"

urlpatterns = [
    path("", views.index, name='index'),
    path("registraition/", views.registraition, name='registraition'),
    path("view/", views.view, name='view'),
    path("startGolf/", views.start_golf, name='start_golf' )
]
