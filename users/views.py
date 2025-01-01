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
from django.views.generic import TemplateView

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from io import BytesIO
from datetime import datetime

def download_receipt(request):
    buffer = BytesIO()
    
    # Document setup
    doc = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Colors
    DARK_BLUE = colors.HexColor('#1e3a8a')
    LIGHT_BLUE = colors.HexColor('#e0f2fe')
    GREEN = colors.HexColor('#10b981')
    GRAY = colors.HexColor('#6b7280')
    BLACK = colors.black
    WHITE = colors.white
    
    # Header section
    doc.setFillColor(DARK_BLUE)
    doc.rect(0, height-2*inch, width, 2*inch, fill=True)
    
    # Header Text
    doc.setFillColor(WHITE)
    doc.setFont("Helvetica-Bold", 24)
    doc.drawCentredString(width/2, height-1.2*inch, "Verification Receipt")
    doc.setFont("Helvetica", 14)
    doc.drawCentredString(width/2, height-1.5*inch, "Official Withdrawal Documentation")
    
    # Verified Badge
    doc.setFillColor(GREEN)
    doc.roundRect(width-2.5*inch, height-1.7*inch, 1.5*inch, 0.4*inch, 6, fill=True)
    doc.setFillColor(WHITE)
    doc.setFont("Helvetica-Bold", 12)
    doc.drawCentredString(width-1.75*inch, height-1.5*inch, "✓ VERIFIED")
    
    # Transaction Details Section
    doc.setFillColor(BLACK)
    doc.setFont("Helvetica-Bold", 16)
    doc.drawString(0.5*inch, height-2.7*inch, "Transaction Details")
    
    # Details Box
    doc.setFillColor(LIGHT_BLUE)
    doc.roundRect(0.5*inch, height-5.2*inch, width-inch, 2*inch, 6, fill=True)
    
    # Transaction Details
    details = [
        ("Transaction ID", f"#{request.user.id}{datetime.now().strftime('%Y%m%d')}"),
        ("Date", datetime.now().strftime('%B %d, %Y')),
        ("Time", datetime.now().strftime('%H:%M:%S')),
        ("Account Holder", request.user.get_full_name()),
        ("Email", request.user.email),
        ("Bank Name", request.user.bank_name),
        ("Account Number", f"****{str(request.user.account_number)[-4:]}"),
        ("Withdrawal Amount", f"${request.user.withdrawal_amount:,.2f}"),
        ("Processing Fee", "$0.00"),
        ("Total Amount", f"${request.user.withdrawal_amount:,.2f}")
    ]
    
    doc.setFont("Helvetica", 11)
    doc.setFillColor(BLACK)
    y_position = height-3.2*inch
    for label, value in details:
        doc.drawString(0.7*inch, y_position, f"{label}:")
        doc.drawString(2.7*inch, y_position, value)
        y_position -= 0.25*inch
    
    # Verification Steps
    doc.setFont("Helvetica-Bold", 16)
    doc.drawString(0.5*inch, height-5.7*inch, "Verification Process Completed")
    
    steps = [
        ("Identity Verification", "Government ID and proof of address verified"),
        ("Tax Compliance", "Tax obligations verified and cleared"),
        ("Security Check", "Two-factor authentication completed"),
        ("Bank Verification", "Account ownership confirmed"),
        ("Final Approval", "Transaction approved by compliance team")
    ]
    
    y_position = height-6.2*inch
    for step, description in steps:
        # Green checkmark
        doc.setFillColor(GREEN)
        doc.setFont("Helvetica-Bold", 14)
        doc.drawString(0.6*inch, y_position, "✓")
        
        # Step title and description
        doc.setFillColor(BLACK)
        doc.setFont("Helvetica-Bold", 11)
        doc.drawString(inch, y_position, step)
        doc.setFont("Helvetica", 9)
        doc.setFillColor(GRAY)
        doc.drawString(inch, y_position-0.2*inch, description)
        y_position -= 0.5*inch
    
    # QR Code for digital verification
    qr_code = qr.QrCodeWidget(f"https://yourcompany.com/verify/{request.user.id}{datetime.now().strftime('%Y%m%d')}")
    qr_drawing = Drawing(1*inch, 1*inch, transform=[1.5,0,0,1.5,0,0])
    qr_drawing.add(qr_code)
    renderPDF.draw(qr_drawing, doc, 6.5*inch, 1.5*inch)
    
    doc.setFillColor(BLACK)
    doc.setFont("Helvetica", 8)
    doc.drawCentredString(7*inch, 1.3*inch, "Scan to verify")
    
    # Signature Section
    doc.setFont("Helvetica-Bold", 12)
    doc.drawString(0.5*inch, 1.2*inch, "Client Signature")
    doc.line(0.5*inch, inch, 3*inch, inch)
    doc.setFont("Helvetica", 10)
    doc.drawString(0.5*inch, 0.8*inch, f"Date: {datetime.now().strftime('%B %d, %Y')}")
    
    # Footer
    doc.setFillColor(DARK_BLUE)
    doc.rect(0, 0, width, 0.6*inch, fill=True)
    doc.setFillColor(WHITE)
    doc.setFont("Helvetica-Bold", 9)
    doc.drawString(0.5*inch, 0.4*inch, "Contact: support@yourcompany.com | +1 (555) 123-4567 | www.yourcompany.com")
    doc.setFont("Helvetica", 7)
    doc.drawString(0.5*inch, 0.2*inch, "This is an automatically generated receipt. Thank you for using our service.")
    
    doc.save()
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="verification_receipt_{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response





@login_required
def receipt_preview(request):
    context = {
        'current_date': datetime.now().strftime('%B %d, %Y'),
        'current_time': datetime.now().strftime('%H:%M:%S'),
        'verification_steps': [
            ("Identity Verification", "Government ID and proof of address verified"),
            ("Tax Compliance", "Tax obligations verified and cleared"),
            ("Security Check", "Two-factor authentication completed"),
            ("Bank Verification", "Account ownership confirmed"),
            ("Final Approval", "Transaction approved by compliance team")
        ]
    }
    return render(request, 'users/receipt_preview.html', context)

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



class TermsOfServiceView(TemplateView):
    template_name = 'users/terms.html'

class HelpCenterView(TemplateView):
    template_name = 'users/help.html'

class SecurityView(TemplateView):
    template_name = 'users/security.html'

