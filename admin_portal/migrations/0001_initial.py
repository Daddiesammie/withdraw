# Generated by Django 5.1.4 on 2024-12-27 07:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_user_account_name_user_account_number_user_balance_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_threshold', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_withdrawal_limit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('document_types_allowed', models.JSONField()),
                ('security_settings', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='AdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create User'), ('verify', 'Verify User'), ('update', 'Update User'), ('delete', 'Delete User'), ('document', 'Document Review')], max_length=20)),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_logs', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('review_notes', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.document')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]