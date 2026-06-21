from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Profile


class CustomRegistrationForm(UserCreationForm):
    """Registration form with role selection and styled fields."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
            'id': 'register-email',
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username',
            'id': 'register-username',
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First name',
            'id': 'register-firstname',
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last name',
            'id': 'register-lastname',
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'id': 'register-password1',
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password',
            'id': 'register-password2',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'password1', 'password2']


class CustomLoginForm(AuthenticationForm):
    """Login form with styled inputs."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email or username',
            'id': 'login-username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'login-password',
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = Profile
        fields = [
            'github_url', 'linkedin_url', 'twitter_url',
            'is_available', 'location',
        ]
        widgets = {
            'github_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/in/...'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://x.com/...'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mumbai, India'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information."""

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'phone', 'website', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 ...'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
        }
