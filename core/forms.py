from django import forms
from django.contrib.auth.models import User
from .models import Profile, Note

class UserRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Ім’я")
    last_name = forms.CharField(max_length=30, required=True, label="Прізвище")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Розкажіть про себе...'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Назва завдання'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Детальний опис завдання'}),
        }