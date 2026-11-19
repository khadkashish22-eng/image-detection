from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()


class EmailChangeForm(forms.ModelForm):
    """Form to handle user email updates with validation."""

    class Meta:
        model = User
        fields = ["email"]  # noqa: RUF012

    def clean_email(self):
        email = self.cleaned_data.get("email").strip().lower()
        if not email:
            raise ValidationError("Email is required.")
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("An account with this email already exists.")
        return email
