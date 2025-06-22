from django import forms
from django.contrib.auth import get_user_model

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['email', 'telephone', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = False
        if commit:
            user.save()
        return user