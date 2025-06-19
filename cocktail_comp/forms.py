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
    CHOICES = [
        ('1', 'Normal')
    ]

    game_type = forms.ChoiceField(label="What type of golf are we playing",choices=CHOICES)
    location = forms.ChoiceField(label="Where is the game beign palyed", choices=CHOICES)
    number_holes = forms.ChoiceField(label="How many holes are being played", choices=holes)
    teams_playing = forms.ModelMultipleChoiceField(label="Which Teams are playing", queryset=Couple.objects.all(), widget=forms.CheckboxSelectMultiple)

class UpdateScoreForm (forms.Form):
    CHOICES = [
        ('0', 'Option 0')
    ]

    score = forms.CharField(label="Score", required=True)

    driver = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        team_members = kwargs.pop('team_members', [])
        super().__init__(*args, **kwargs)

        self.fields['driver'].choices = [(member, member) for member in team_members]

    mulligan = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    milligan = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    milligan_choice = forms.CharField(required=False, max_length=100)

class UserLoginForm (forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    password = forms.CharField(label="Password", max_length=100)
    
class UserRegistrationForm (forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    password = forms.CharField(label="Password", max_length=100)

class JoinTeamForm (forms.Form):
    name = forms.CharField(label="testing")


class TeamUpdateForm (forms.Form):
    def CHOICES():
        teams = Couple.objects.filter().all()
        choices = [(team.team, team.team) for i,team in enumerate(teams)]
        print(choices)
        # for item in teams:
        #     choices.append((f"{item}", f"{item}"))
        #     print(item)
        return choices

    team_name = forms.ChoiceField(label="What team are you looking to join/make adjustments for?",
                                  choices=CHOICES())
    
class StartCompetitionForm (forms.Form):
    CHOICES = [
        ('1', 'Normal')
    ]

    date = forms.DateTimeField(label="What Day?")
    # Golf Details
    game_type = forms.ChoiceField(label="What type of golf are we playing",choices=CHOICES)
    location = forms.ChoiceField(label="Where is the game beign palyed", choices=CHOICES)
    number_holes = forms.ChoiceField(label="How many holes are being played", choices=holes)
    teams_playing = forms.ModelMultipleChoiceField(label="Which Teams are playing", queryset=Couple.objects.all(), widget=forms.CheckboxSelectMultiple)
    # Cocktails Details if needed
    