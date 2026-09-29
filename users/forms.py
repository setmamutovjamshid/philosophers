import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class SignUpForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=100,
        required=True,
        label="To'liq ism",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ali Valiyev',
                'class': (
                    'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                    'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                    'focus:ring-blue-100 transition-all'
                ),
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Elektron pochta",
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'ali@misol.uz',
                'class': (
                    'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                    'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                    'focus:ring-blue-100 transition-all'
                ),
            }
        ),
    )

    username = forms.CharField(
        max_length=30,
        required=True,
        label="Foydalanuvchi nomi (Username)",
        widget=forms.TextInput(
            attrs={
                'placeholder': 'ali_valiyev',
                'class': (
                    'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                    'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                    'focus:ring-blue-100 transition-all'
                ),
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ('full_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = "Parol"
        self.fields['password1'].widget.attrs.update({
            'placeholder': '••••••••',
            'class': (
                'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                'focus:ring-blue-100 transition-all'
            ),
            'id': 'id_password1',
        })
        self.fields['password2'].label = "Parolni tasdiqlang"
        self.fields['password2'].widget.attrs.update({
            'placeholder': '••••••••',
            'class': (
                'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                'focus:ring-blue-100 transition-all'
            ),
            'id': 'id_password2',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Bu email manzili bilan allaqachon hisob ochilgan.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
            if not re.search(r'[a-zA-Z]', password1):
                raise ValidationError("Parolda kamida bitta harf bo'lishi shart.")
            if not re.search(r'[0-9]', password1):
                raise ValidationError("Parolda kamida bitta raqam bo'lishi shart.")
        return password1

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        parts = full_name.split(maxsplit=1)
        user.first_name = parts[0] if parts else ''
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Foydalanuvchi nomi"
        self.fields['username'].widget.attrs.update({
            'placeholder': 'ali_valiyev',
            'class': (
                'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                'focus:ring-blue-100 transition-all'
            ),
        })
        self.fields['password'].label = "Parol"
        self.fields['password'].widget.attrs.update({
            'placeholder': '••••••••',
            'class': (
                'w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm text-slate-900 '
                'placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 '
                'focus:ring-blue-100 transition-all'
            ),
        })
