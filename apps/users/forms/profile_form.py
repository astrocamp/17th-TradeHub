from django import forms
from ..models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'department', 'title', 'email', 'hire_date', 'username', 'birthday', 'phone', 'address', 'note']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'department': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'title': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control border px-2 py-1'}),
            'username': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control border px-2 py-1'}),
            'phone': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'address': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
            'note': forms.TextInput(attrs={'class': 'form-control border px-2 py-1'}),
        }
        labels = {
            'first_name': 'Name',
            'department': 'Department',
            'title': 'Title',
            'email': 'Email',
            'hire_date': 'Hire Date',
            'username': 'Username',
        }