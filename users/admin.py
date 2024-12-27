from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Document, VerificationStatus

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email', 
        'username', 
        'withdrawal_amount',
        'balance',
        'is_verified', 
        'verification_progress'
    )
    
    list_filter = ('is_verified', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 
                'last_name', 
                'email',
                'phone_number'
            )
        }),
        ('Account Details', {
            'fields': (
                'account_number',
                'bank_name',
                'account_name',
                'balance',
                'withdrawal_amount'
            )
        }),
        ('Verification Codes', {
            'fields': (
                'withdrawal_otp',
                'tax_verification_code',
                'identity_verification_code',
                'final_verification_code'
            )
        }),
        ('Status', {
            'fields': (
                'is_verified',
                'verification_progress'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )

admin.site.register(Document)
admin.site.register(VerificationStatus)
