from django.db import models

# Create your models here.
# class User (models.Model):
#     name = models.CharField(max_length=200)
#     partner = models.CharField(max_length=200)

class Couple (models.Model):
    team = models.CharField(max_length=200)
    partner_names = models.CharField(max_length=200)
    golf_results = models.CharField(max_length=200, null=True)
    cocktail_results = models.CharField(max_length=200, null=True)
    past_results = models.CharField(max_length=200, null=True)

# class GolfCard (models.Model):
#     location = models.CharField(max_length=200)
#     game_type = models.CharField(max_length=200)
#     number_holes = models.IntegerField(max_length=200)
#     results = models.