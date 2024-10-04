from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as CustomUserAdmin
from .models import User


# Register your models here.

class UserAdmin(CustomUserAdmin):
    model = User
    list_display = ('email', 'username', 'is_staff')


admin.site.register(User, UserAdmin)
