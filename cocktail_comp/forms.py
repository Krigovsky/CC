from django import forms
from .models import Couple


holes = (
            ("9", "Nine"),
            ("18", "Eighteen")
        )
class RegisterForm (forms.Form):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team_name'].widget.attrs['class'] = 'form-control'
        self.fields['partner_names'].widget.attrs['class'] = 'form-control'
        # self.fields['team_name'].widget.attrs['class'] = 'form-label'

    team_name = forms.CharField(label="What is your Team Name", max_length=50)
    partner_names = forms.CharField(label="Names of the couple, seperated by comma", max_length=100)

class StartGolfGameForm (forms.Form):

    game_type = forms.CharField(label="What type of golf are we playing", max_length=50)
    location = forms.CharField(label="Where is the game beign palyed", max_length=50)
    number_holes = forms.ChoiceField(label="How many holes are being played", choices=holes)
    teams_playing = forms.ModelMultipleChoiceField(label="Which Teams are playing", queryset=Couple.objects.all(), widget=forms.CheckboxSelectMultiple)

class UpdateScoreForm (forms.Form):
    score = forms.CharField(label="Testing")
