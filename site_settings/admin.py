from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'email', 'phone']
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_logo', 'about')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance of settings
        return not SiteSettings.objects.exists()
