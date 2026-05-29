from django import forms
from .models import Post, Comment, Category, Tag


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""

    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'python, django, web-dev (comma separated)',
            'id': 'post-tags',
        }),
        help_text='Enter tags separated by commas',
    )

    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'featured_image',
            'category', 'status', 'is_premium', 'is_featured',
            'meta_title', 'meta_description', 'project_live_url', 'project_price',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input form-input-lg',
                'placeholder': 'Enter your post title...',
                'id': 'post-title',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Brief summary of your post...',
                'id': 'post-excerpt',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
                'id': 'post-category',
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
                'id': 'post-status',
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'id': 'post-image',
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'SEO title (max 60 chars)',
                'maxlength': 60,
                'id': 'post-meta-title',
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'SEO description (max 160 chars)',
                'maxlength': 160,
                'id': 'post-meta-desc',
            }),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'project_live_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://example.com',
                'id': 'project-live-url',
            }),
            'project_price': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., $500, Fixed, Custom',
                'id': 'project-price',
            }),
        }

    def save(self, commit=True):
        post = super().save(commit=commit)
        if commit:
            # Handle tags
            tags_str = self.cleaned_data.get('tags_input', '')
            if tags_str:
                tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
                post.tags.clear()
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(
                        name=name,
                        defaults={'slug': name.lower().replace(' ', '-')}
                    )
                    post.tags.add(tag)
        return post


class CommentForm(forms.ModelForm):
    """Form for blog post comments."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Share your thoughts...',
                'id': 'comment-content',
                'maxlength': 1000,
            }),
        }


class SearchForm(forms.Form):
    """Blog search form."""

    q = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Search posts...',
            'id': 'search-input',
            'autocomplete': 'off',
        })
    )
