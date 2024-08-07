from django.contrib import admin
from accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'birth_date', 'created_at', 'profile_picture')
    search_fields = ('user__username', 'job')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'job', 'birth_date', 'bio', 'profile_picture')}),
        ('Additional Info', {'fields': ('created_at',)}),
    )
# Register your models here.
