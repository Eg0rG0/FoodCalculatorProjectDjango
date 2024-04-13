from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm

from .models import FoodCart, CustomUser, Food


class CustomUserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(max_length=25, label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=25, label='Confirm Password', widget=forms.PasswordInput)

    error_messages = {
        "password_mismatch": "Брат мой, пароли не совпадают, я проверил два раза, честно",
    }

    def clean_username(self):
        valid_chars = ("1234567890abcdefghijklmnopqrstuvwxyz"
                       "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                       "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                       "ЯЮЭЬЫЪЩШЧЦХФУТСРПОНМЛКЙИЗЖЁЕДГВБА")
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            self.add_error("username", "Дружище, такое имя пользователя уже есть, придется выбрать другое")
        if not all(char in valid_chars for char in str(username)):
            self.add_error("username", "Братан, можно только буквы и цифры, другое никак, сорян :(")
        return username

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserSingUpForm(AuthenticationForm):
    username = forms.CharField(max_length=25, label='Username')
    password = forms.CharField(max_length=25, label='Password', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not CustomUser.objects.filter(username=username).exists():
            self.add_error("username", "Дружище, так ты не зарегался, такого логина нет")

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                self.add_error("password", "А пароль то не тот")
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class FoodCreationForm(forms.ModelForm):
    food_name = forms.CharField(label="food_name")
    fats = forms.FloatField(label="fats")
    carbs = forms.FloatField(label="carbs")
    proteins = forms.FloatField(label="proteins")

    class Meta:
        model = Food
        fields = ["food_name", "fats", "carbs", "proteins"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "password", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def clean_password(self):
        return self.initial.get("password")

    def save(self, commit=True):
        instance = super(CustomUserChangeForm, self).save(commit=False)
        changed_fields = set()
        for field_name, field_value in self.cleaned_data.items():
            if field_name != "password" and field_value != getattr(instance, field_name):
                setattr(instance, field_name, field_value)
                changed_fields.add(field_name)
        if commit:
            instance.save()
        return instance, changed_fields


class FoodCartCreationForm(forms.ModelForm):
    class Meta:
        model = FoodCart
        fields = ["name", "foods"]
        widgets = {
            'foods': forms.SelectMultiple(attrs={'size': 5}),
        }


class FoodCartChangeForm(forms.ModelForm):
    class Meta:
        model = FoodCart
        fields = ['foods']
        widgets = {
            'foods': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foods'].queryset = Food.objects.all()

