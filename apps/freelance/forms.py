from django import forms
from .models import Project, Bid, Review, Milestone


class ProjectForm(forms.ModelForm):
    """Form for creating/editing freelance projects."""

    skills_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Python, Django, React (comma separated)',
        }),
    )

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'category', 'budget_type',
            'budget_min', 'budget_max', 'deadline', 'attachment',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 6, 'placeholder': 'Describe your project...'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'budget_type': forms.Select(attrs={'class': 'form-input'}),
            'budget_min': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '5000'}),
            'budget_max': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '25000'}),
            'deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'attachment': forms.FileInput(attrs={'class': 'form-file-input'}),
        }

    def save(self, commit=True):
        project = super().save(commit=False)
        skills_str = self.cleaned_data.get('skills_input', '')
        if skills_str:
            project.skills_required = [s.strip() for s in skills_str.split(',') if s.strip()]
        if commit:
            project.save()
        return project


class BidForm(forms.ModelForm):
    """Form for submitting a bid on a project."""

    class Meta:
        model = Bid
        fields = ['amount', 'delivery_days', 'proposal']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Your bid amount (₹)'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Delivery in days'}),
            'proposal': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': 'Explain why you are the best fit for this project...',
            }),
        }


class ReviewForm(forms.ModelForm):
    """Form for submitting a review."""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Share your experience...',
            }),
        }


class MilestoneForm(forms.ModelForm):
    """Form for creating milestones."""

    class Meta:
        model = Milestone
        fields = ['title', 'description', 'amount', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Milestone title'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Amount (₹)'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
