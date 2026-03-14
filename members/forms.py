from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from home.models import Player

class CustomUserCreationForm(UserCreationForm):
    SKILL_CHOICES = [
         ("Beginner","Beginner"),
         ("Intermediate","Intermediate"),
         ("Advanced","Advanced"),
    ]
    email = forms.EmailField(required = True)
    skill_level = forms.ChoiceField(required = True, choices= SKILL_CHOICES)
    keyword = forms.CharField(max_length=100, help_text= "Enter the club keyword.")
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "skill_level",
            "keyword",
        ]
    def clean_email(self):
            email = self.cleaned_data.get('email')

            #check if email already exists in the database
            if User.objects.filter(email = email).exists():
                # if i does, raise an error to be displayed to the user
                raise forms.ValidationError('This email is already registered. Please use a different one.')


                #if the email is valid thus far, return it
            return email
    def clean_keyword(self):
         keyword = self.cleaned_data.get('keyword')
         if keyword != settings.CLUB_JOIN_KEYWORD:
              raise forms.ValidationError("Invalid club keyword.")
         return keyword

    def save(self, commit = True):
        user = super().save(commit= commit)
        skill = self.cleaned_data.get('skill_level')
        starting_rank = {
        "Beginner": 450,
        "Intermediate": 550,
        "Advanced": 650,
        }[skill]
        Player.objects.create(user = user, first = user.first_name, last = user.last_name, rank = starting_rank)
        return user
         
    