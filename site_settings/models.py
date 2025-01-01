from django.db import models
from django.core.cache import cache

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100)
    site_logo = models.ImageField(upload_to='site_logo/')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    about = models.TextField()
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache when settings are updated
        cache.delete('site_settings')
    
    @classmethod
    def get_settings(cls):
        # Get settings from cache or database
        settings = cache.get('site_settings')
        if not settings:
            settings = cls.objects.first()
            cache.set('site_settings', settings)
        return settings

