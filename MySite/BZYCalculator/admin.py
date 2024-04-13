from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserRegistrationForm, CustomUserSingUpForm, CustomUserChangeForm
from .models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserRegistrationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["username", "first_name", "last_name", "email"]

    filter_horizontal = ()
    list_filter = ()

    fieldsets = (
        (None, {"fields": ("username", "first_name", "last_name", "email")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
