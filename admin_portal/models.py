from django.db import models
from users.models import User, Document, VerificationStatus

class AdminLog(models.Model):
    ACTIONS = (
        ('create', 'Create User'),
        ('verify', 'Verify User'),
        ('update', 'Update User'),
        ('delete', 'Delete User'),
        ('document', 'Document Review'),
    )
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=20, choices=ACTIONS)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_logs')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

class DocumentReview(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now=True)

class AdminSettings(models.Model):
    verification_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    max_withdrawal_limit = models.DecimalField(max_digits=10, decimal_places=2)
    document_types_allowed = models.JSONField()
    security_settings = models.JSONField()