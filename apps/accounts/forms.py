from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Profile


class CustomRegistrationForm(UserCreationForm):
    """Registration form with role selection and styled fields."""

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if field_name == 'first_name':
                field.widget.attrs['placeholder'] = 'First name'
            elif field_name == 'last_name':
                field.widget.attrs['placeholder'] = 'Last name'
            elif field_name == 'email':
                field.widget.attrs['placeholder'] = 'your@email.com'
            elif field_name == 'username':
                field.widget.attrs['placeholder'] = 'Choose a username'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Create a password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm password'


class CustomLoginForm(AuthenticationForm):
    """Login form with styled inputs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Email or username'
                field.widget.attrs['autofocus'] = True
            elif field_name == 'password':
                field.widget.attrs['placeholder'] = 'Password'


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = Profile
        fields = [
            'github_url', 'linkedin_url', 'twitter_url',
            'is_available', 'location',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-checkbox'
            else:
                field.widget.attrs['class'] = 'form-input'
            
            if field_name == 'github_url':
                field.widget.attrs['placeholder'] = 'https://github.com/...'
            elif field_name == 'linkedin_url':
                field.widget.attrs['placeholder'] = 'https://linkedin.com/in/...'
            elif field_name == 'twitter_url':
                field.widget.attrs['placeholder'] = 'https://x.com/...'
            elif field_name == 'location':
                field.widget.attrs['placeholder'] = 'Mumbai, India'


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information."""

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'phone', 'website', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-file-input'
                field.widget.attrs['accept'] = 'image/*'
            else:
                field.widget.attrs['class'] = 'form-input'
            
            if field_name == 'bio':
                field.widget.attrs['rows'] = 4
                field.widget.attrs['placeholder'] = 'Tell us about yourself...'
            elif field_name == 'phone':
                field.widget.attrs['placeholder'] = '+91 ...'
            elif field_name == 'website':
                field.widget.attrs['placeholder'] = 'https://...'
