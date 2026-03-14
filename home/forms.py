from django import forms
from .models import Match, Player
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate

class MatchForm(forms.ModelForm):
    OPPONENT_CHOICES = Player.objects.all()
    MATCH_TYPE_CHOICES = [
        ("Mixed Singles","Mixed Singles"),
        ("Women's Singles","Women's Singles"),
        ("Men's Singles","Men's Singles"),
    ]
    WIN_CHOICES = [
        ("Yes","Yes"),
        ("No","No")
    ]
    opponent = forms.ModelChoiceField(required = True, queryset=OPPONENT_CHOICES)
    match_type = forms.ChoiceField(required = True, choices=MATCH_TYPE_CHOICES)
    win = forms.ChoiceField(required = True, choices= WIN_CHOICES)
    opponent_password = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=100,
        help_text="Have your opponent enter their password."
    )
    class Meta:

        model = Match

        fields= [
            "opponent",
            "match_type",
            "win",
            #"opponent_password",

        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            player = Player.objects.get(user=self.user)
            self.fields["opponent"].queryset = (Player.objects.filter(user__is_active = True).exclude(pk=player.pk).order_by('first'))


    def clean_opponent_password(self):
        opponent = self.cleaned_data.get('opponent')
        opponent_password = self.cleaned_data.get('opponent_password')
        if not check_password(opponent_password, opponent.user.password):
            raise forms.ValidationError("Incorrect Opponent Password")

        return opponent_password
    def save(self, commit = True):
        match = super().save(commit = False)
        match.player1 = Player.objects.get(user = self.user)

        match.player2 = self.cleaned_data.get('opponent')

        match.match_type = self.cleaned_data.get('match_type')

        if self.cleaned_data.get('win') == 'Yes':
            match.winner = match.player1
            match.player1.wins += 1

        else:
            match.winner = match.player2
            match.player2.wins += 1

        if commit:
            #get expected win probabilities for both players
            expected_1 = exp_win1(match.player1, match.player2)
            expected_2 = 1 - expected_1
            #get proper k factors for both players
            kfact1 = get_kfactor(match.player1, match)
            kfact2 = get_kfactor(match.player2, match)
            #distribute points
            if match.winner == match.player1:
                temp = match.player1.rank
                match.player1.rank = match.player1.rank + kfact1 * (1 - expected_1)
                match.player1Effect = match.player1.rank - temp

                temp = match.player2.rank
                match.player2.rank = match.player2.rank + kfact2 * (0 - expected_2)
                match.player2Effect = match.player2.rank - temp
            else:
                temp = match.player2.rank
                match.player2.rank = match.player2.rank + kfact2 * (1 - expected_2)
                match.player2Effect = match.player2.rank - temp

                temp = match.player1.rank
                match.player1.rank = match.player1.rank + kfact1 * (0 - expected_1)
                match.player1Effect = match.player1.rank - temp
                
            match.player1.matches  += 1
            match.player2.matches  += 1
            match.player1.save()
            match.player2.save()
            match.save()

        return match

def kfactor_mult(match):
    if match.match_type == "Mixed Singles":
        return 1
    elif match.match_type == "Women's Singles":
        return 1.25
    else:
        return 1.5
def get_kfactor(player, match):
    if player.matches <= 2:
        return 48 * kfactor_mult(match)
    elif player.matches <= 4:
        return 40 * kfactor_mult(match)
    elif player.matches <=7:
        return 32 * kfactor_mult(match)
    elif player.matches <=14:
        return 24 * kfactor_mult(match)
    else:
        return 16 * kfactor_mult(match)
def exp_win1(player1,player2):
    denom = 1 + 10**((player2.rank - player1.rank)/400)
    exp = 1/denom
    return exp
class LeaveForm(forms.Form):
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(), help_text='Enter your password')
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(), help_text='Confirm Password')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')

        if pw1 != pw2:
            raise forms.ValidationError('Passwords do not match.')
        if not authenticate(username = self.user.username, password = pw1):
            raise forms.ValidationError('Incorrect password.')

        return cleaned_data


