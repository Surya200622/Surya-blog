from django import forms


class ContactForm(forms.Form):
    """Contact page form."""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Your name',
            'id': 'contact-name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com',
            'id': 'contact-email',
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Subject',
            'id': 'contact-subject',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 5,
            'placeholder': 'Your message...',
            'id': 'contact-message',
        })
    )
