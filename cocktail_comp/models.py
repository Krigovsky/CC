from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
# class User (models.Model):
#     name = models.CharField(max_length=200)
#     partner = models.CharField(max_length=200)

class Couple (models.Model):
    def __str__(self) -> str:
         return self.team
    team = models.CharField(max_length=200)
    partner_names = models.CharField(max_length=200)
    golf_results = models.CharField(max_length=200, null=True)
    cocktail_results = models.CharField(max_length=200, null=True)
    past_results = models.CharField(max_length=200, null=True)

class GolfGame (models.Model):

    # class NumHoles (models.TextChoices):
    date = models.DateTimeField()

    game_type = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    number_holes = models.IntegerField()
    teams_playing = models.CharField(max_length=200)

class GolfCard (models.Model):

    card = models.ForeignKey(GolfGame, on_delete=models.CASCADE, null=True)
    results = models.CharField(max_length=200)
