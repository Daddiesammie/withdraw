from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import random
import string

class User(AbstractUser):
    email = models.EmailField(unique=True)
    withdrawal_otp = models.CharField(max_length=10, blank=True, null=True)
    tax_verification_code = models.CharField(max_length=10, blank=True, null=True)
    identity_verification_code = models.CharField(max_length=10, blank=True, null=True)
    final_verification_code = models.CharField(max_length=10, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_progress = models.IntegerField(default=0)

    withdrawal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.email
    

    def generate_verification_code(self):
        """Generate a random 6-digit code"""
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate codes for new users
            self.withdrawal_otp = self.generate_verification_code()
            self.tax_verification_code = self.generate_verification_code()
            self.identity_verification_code = self.generate_verification_code()
            self.final_verification_code = self.generate_verification_code()
        super().save(*args, **kwargs)

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email}'s document"

class VerificationStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    withdrawal_verified = models.BooleanField(default=False)
    tax_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    final_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email}'s verification status"
