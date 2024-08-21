from django import forms

class RegisterForm (forms.Form):
    team_name = forms.CharField(label="What is your Team Name", max_length=50)