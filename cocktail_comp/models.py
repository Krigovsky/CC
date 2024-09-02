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
        
        


    game_type = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    number_holes = models.CharField(max_length=200)
    teams_playing = models.ForeignKey(Couple, on_delete=models.CASCADE)

class GolfCard (models.Model):

    team_id = models.ForeignKey(Couple, on_delete=models.CASCADE)
    results = models.IntegerField()