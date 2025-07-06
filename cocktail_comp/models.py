from django.db import models
from django.utils.translation import gettext_lazy as _


class User (models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

class Couple (models.Model):
    
    def __str__(self) -> str:
         return self.team
    
    team = models.CharField(max_length=200, unique=True)
    partner_names = models.CharField(max_length=200)
    golf_results = models.CharField(max_length=200, null=True)
    cocktail_results = models.CharField(max_length=200, null=True)
    past_results = models.CharField(max_length=200, null=True)

class GolfGame (models.Model):
    def __str__(self):
        return self.id

    # class NumHoles (models.TextChoices):
    date = models.DateTimeField()

    game_type = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    number_holes = models.IntegerField()
    teams_playing = models.CharField(max_length=200)

class GolfCard (models.Model):

    card = models.ForeignKey(GolfGame, on_delete=models.CASCADE, null=True)
    team_count = models.IntegerField()
    results = models.CharField(max_length=200)
    driver_count = models.CharField(max_length=200)
    current_hole = models.IntegerField(default=0)
    score = models.CharField(max_length=200)
    card_driver = models.CharField(max_length=200)
    over_drivers = models.CharField(max_length=200, default=[])
    allowed_drivers = models.CharField(max_length=200, default=[])

    powers = models.CharField(max_length=200, default={})

class Cocktail (models.Model):
    def __str__(self):
        return f"""Cocktail 
    Team: {self.team}
    name: {self.cocktail_name} 
"""
    date = models.DateField()
    team = models.ForeignKey(Couple, on_delete=models.CASCADE, null=True)
    cocktail_name = models.CharField(max_length=255, null=True)
    alcohol_base = models.CharField(max_length=255, null=True)
    mixers = models.CharField(max_length=255, null=True)
    garnish = models.CharField(max_length=250)
    total_score = models.CharField(max_length=250, null=True)

class CocktailCard (models.Model):
    def __str__(self):
        return f"""Cocktail Card
    Teams: {self.teams}
    Order: {self.order}    
"""
    teams = models.CharField(max_length=200)
    presentation_score = models.CharField(max_length=500, null=True)
    presentation_comments = models.TextField(null=True)
    taste_score = models.CharField(max_length=500, null=True)
    taste_comments = models.TextField(null=True)
    creativity_score = models.CharField(max_length=500, null=True)
    creativity_comments = models.TextField(null=True)
    theme_score = models.CharField(max_length=500, null=True)
    theme_comments = models.TextField(null=True)
    drinkability_score = models.CharField(max_length=500, null=True)
    drinkability_comments = models.TextField(null=True)
    total = models.CharField(max_length=500, null=True)
    order = models.CharField(max_length=500, null=True)
    current_index = models.IntegerField(default=0)
    cocktail_list = models.CharField(max_length=255, null=True)
    
class CompetitionStart (models.Model):

    date = models.DateField()
    teams = models.CharField(max_length=200)
    golf_card = models.ForeignKey(GolfCard, on_delete=models.CASCADE, null=True)
    cocktail_card = models.ForeignKey(CocktailCard, on_delete=models.CASCADE, null=True)

