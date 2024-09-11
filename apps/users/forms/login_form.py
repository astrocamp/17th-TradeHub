from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username == "":
            self.add_error("username", "Username is required.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password == "":
            self.add_error("password", "Password is required.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)

        if username and password:
            if user is None:
                raise forms.ValidationError("Invalid username or password.")

        return cleaned_data
