from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Account


# Register your models here.


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username','last_name','first_name', 'last_login', 'is_admin', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name',)
    search_fields = ('email', 'username',)
    readonly_fields = ('id', 'last_login','date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    list_per_page = 10






admin.site.register(Account, UserAdmin)
