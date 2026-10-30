
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Електронна пошта",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введіть електронну пошту",
        }),
    )

    username = forms.CharField(
        label="Ім'я користувача",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Придумайте ім'я користувача",
        }),
    )

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Створіть пароль",
        }),
    )

    password2 = forms.CharField(
        label="Підтвердження пароля",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Повторіть пароль",
        }),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Користувач із такою електронною поштою вже існує."
            )

        return email

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "age",
            "gender",
            "height",
            "weight",
            "activity_level",
            "goal",
        ]

        widgets = {
            "age": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "120",
                "placeholder": "Наприклад, 22",
            }),
            "gender": forms.Select(attrs={
                "class": "form-select",
            }),
            "height": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "300",
                "step": "0.1",
                "placeholder": "Наприклад, 170",
            }),
            "weight": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "max": "700",
                "step": "0.1",
                "placeholder": "Наприклад, 65",
            }),
            "activity_level": forms.Select(attrs={
                "class": "form-select",
            }),
            "goal": forms.Select(attrs={
                "class": "form-select",
            }),
        }

        labels = {
            "age": "Вік",
            "gender": "Стать",
            "height": "Зріст (см)",
            "weight": "Маса тіла (кг)",
            "activity_level": "Рівень фізичної активності",
            "goal": "Мета харчування",
        }

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and not 1 <= age <= 120:
            raise forms.ValidationError(
                "Вік повинен бути від 1 до 120 років."
            )
        return age

    def clean_height(self):
        height = self.cleaned_data.get("height")
        if height is not None and not 1 <= height <= 300:
            raise forms.ValidationError(
                "Зріст повинен бути від 1 до 300 см."
            )
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None and not 1 <= weight <= 700:
            raise forms.ValidationError(
                "Маса тіла повинна бути від 1 до 700 кг."
            )
        return weight
