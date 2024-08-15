from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class UserRegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(label="confrim password", widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError("this email alredy exists")
        return email
    
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        user = User.objects.filter(username=username)
        if user:
            raise ValidationError("this username is alredy exists")
        return username
    
    
    def clean(self):
        cd = super().clean()
        password1 = cd.get("password")
        password2 = cd.get("confirm_password")

        if password1 and password2 and password1 != password2:
            raise ValidationError("passwords must match ")
        
        
class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username or email", widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

    
class EditUserProfile(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ("age", "bio")