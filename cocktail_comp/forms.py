from django import forms

class RegisterForm (forms.Form):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team_name'].widget.attrs['class'] = 'form-control'
        self.fields['partner_names'].widget.attrs['class'] = 'form-control'
        # self.fields['team_name'].widget.attrs['class'] = 'form-label'

    team_name = forms.CharField(label="What is your Team Name", max_length=50)
    partner_names = forms.CharField(label="Names of the couple, seperated by comma", max_length=100)