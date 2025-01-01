from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.verification_home, name='verification_home'),
    path('withdrawal-verification/', views.withdrawal_verification, name='withdrawal_verification'),
    path('tax-verification/', views.tax_verification, name='tax_verification'),
    path('identity-verification/', views.identity_verification, name='identity_verification'),
    path('final-verification/', views.final_verification, name='final_verification'),
    path('verification-complete/', views.verification_complete, name='verification_complete'),
    path('download-receipt/', views.download_receipt, name='download_receipt'),
    path('receipt/preview/', views.receipt_preview, name='receipt_preview'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    path('help/', views.HelpCenterView.as_view(), name='help'),
    path('security/', views.SecurityView.as_view(), name='security'),
]
