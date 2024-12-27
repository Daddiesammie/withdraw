from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Document, VerificationStatus
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def download_receipt(request):
    buffer = BytesIO()
    
    # Set up the document
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add company logo/header background
    p.setFillColorRGB(0.23, 0.35, 0.60)  # Dark blue
    p.rect(0, height-2*inch, width, 2*inch, fill=1)
    
    # Header text
    p.setFillColorRGB(1, 1, 1)  # White
    p.setFont("Helvetica-Bold", 28)
    p.drawString(50, height-1.2*inch, "Verification Receipt")
    
    # Add decorative elements
    p.setFillColorRGB(0.23, 0.35, 0.60)  # Dark blue
    p.rect(50, height-2.3*inch, width-100, 2, fill=1)
    
    # Transaction details section
    p.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height-3*inch, "Transaction Details")
    
    # Details box
    p.setStrokeColorRGB(0.9, 0.9, 0.9)  # Light gray
    p.rect(50, height-5*inch, width-100, 1.5*inch)
    
    # Transaction information
    p.setFont("Helvetica", 12)
    details = [
        f"Transaction ID: #{request.user.id}{datetime.now().strftime('%Y%m%d')}",
        f"Date: {datetime.now().strftime('%B %d, %Y')}",
        f"Account Holder: {request.user.get_full_name()}",
        f"Email: {request.user.email}",
        f"Withdrawal Amount: ${request.user.withdrawal_amount:,.2f}"
    ]
    
    y_position = height-3.3*inch
    for detail in details:
        p.drawString(70, y_position, detail)
        y_position -= 20
    
    # Status indicator
    p.setFillColorRGB(0.13, 0.55, 0.13)  # Green
    p.roundRect(width-200, height-3.3*inch, 130, 25, 12, fill=1)
    p.setFillColorRGB(1, 1, 1)  # White
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width-180, height-3*inch, "✓ VERIFIED")
    
    # Verification steps section
    p.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height-5.5*inch, "Completed Verification Steps")
    
    # Steps with checkmarks
    steps = [
        "Withdrawal OTP Verification",
        "Tax Verification",
        "Identity Verification",
        "Final Verification"
    ]
    
    y_position = height-6*inch
    p.setFont("Helvetica", 12)
    for step in steps:
        p.setFillColorRGB(0.13, 0.55, 0.13)  # Green
        p.drawString(70, y_position, "✓")
        p.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
        p.drawString(90, y_position, step)
        y_position -= 25
    
    # Footer
    p.setFillColorRGB(0.23, 0.35, 0.60)  # Dark blue
    p.rect(0, 0, width, 1*inch, fill=1)
    p.setFillColorRGB(1, 1, 1)  # White
    p.setFont("Helvetica", 10)
    p.drawString(50, 0.5*inch, "This is an automatically generated receipt. Thank you for using our service.")
    
    # QR Code placeholder (you can add an actual QR code here)
    p.setStrokeColorRGB(1, 1, 1)
    p.rect(width-100, 0.25*inch, 0.5*inch, 0.5*inch, stroke=1)
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="verification_receipt_{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response



def verification_home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        status = VerificationStatus.objects.get(user=request.user)
    except VerificationStatus.DoesNotExist:
        status = VerificationStatus.objects.create(user=request.user)
    
    context = {
        'progress': request.user.verification_progress,
        'status': status
    }
    return render(request, 'users/verification_home.html', context)

@login_required
def withdrawal_verification(request):
    if request.method == 'POST':
        otp = request.POST.get('withdrawal_otp')
        if otp == request.user.withdrawal_otp:
            status = VerificationStatus.objects.get(user=request.user)
            status.withdrawal_verified = True
            status.save()
            request.user.verification_progress = 25
            request.user.save()
            messages.success(request, 'Withdrawal OTP verified successfully!')
            return redirect('users:tax_verification')
        messages.error(request, 'Invalid OTP')
    return render(request, 'users/withdrawal_verification.html')

@login_required
def tax_verification(request):
    if request.method == 'POST':
        code = request.POST.get('tax_code')
        if code == request.user.tax_verification_code:
            status = VerificationStatus.objects.get(user=request.user)
            status.tax_verified = True
            status.save()
            request.user.verification_progress = 50
            request.user.save()
            messages.success(request, 'Tax verification completed successfully!')
            return redirect('users:identity_verification')
        messages.error(request, 'Invalid verification code')
    return render(request, 'users/tax_verification.html')

@login_required
def identity_verification(request):
    if request.method == 'POST':
        document = request.FILES.get('document')
        code = request.POST.get('identity_code')
        
        if document:
            Document.objects.create(user=request.user, document=document)
        
        if code == request.user.identity_verification_code:
            status = VerificationStatus.objects.get(user=request.user)
            status.identity_verified = True
            status.save()
            request.user.verification_progress = 75
            request.user.save()
            messages.success(request, 'Identity verification completed successfully!')
            return redirect('users:final_verification')
        messages.error(request, 'Invalid verification code')
    return render(request, 'users/identity_verification.html')

@login_required
def final_verification(request):
    if request.method == 'POST':
        code = request.POST.get('final_code')
        if code == request.user.final_verification_code:
            status = VerificationStatus.objects.get(user=request.user)
            status.final_verified = True
            status.save()
            request.user.verification_progress = 100
            request.user.is_verified = True
            request.user.save()
            messages.success(request, 'Final verification completed successfully!')
            return redirect('users:verification_complete')
        messages.error(request, 'Invalid verification code')
    return render(request, 'users/final_verification.html')

@login_required
def verification_complete(request):
    return render(request, 'users/verification_complete.html')




