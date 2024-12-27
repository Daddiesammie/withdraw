from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.models import User, Document, VerificationStatus
from .models import AdminLog, DocumentReview
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login, get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import get_backends

@staff_member_required
def login_as_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    # Store admin session data
    request.session['admin_id'] = request.user.id
    
    # Get the first available backend
    backend = get_backends()[0]
    
    # Set the backend and login
    user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
    login(request, user)
    
    # Log this action
    AdminLog.objects.create(
        admin_id=request.session['admin_id'],
        action='login_as_user',
        target_user=user,
        description=f'Admin logged in as user {user.email}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'You are now logged in as {user.email}')
    return redirect('users:dashboard')



@staff_member_required
def create_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create verification status for new user
        VerificationStatus.objects.create(user=user)
        
        messages.success(request, f'User {username} created successfully')
        return redirect('admin_portal:user_list')
        
    return render(request, 'admin_portal/create_user.html')


@staff_member_required
def dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'pending_verifications': User.objects.filter(is_verified=False).count(),
        'total_withdrawals': User.objects.aggregate(Sum('withdrawal_amount'))['withdrawal_amount__sum'],
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'pending_documents': Document.objects.filter(documentreview__status='pending').count()
    }
    return render(request, 'admin_portal/dashboard.html', context)

@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'total_users': users.count(),
        'verified_users': users.filter(is_verified=True).count()
    }
    return render(request, 'admin_portal/user_list.html', context)

@staff_member_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    verification_status = VerificationStatus.objects.get_or_create(user=user)[0]
    documents = Document.objects.filter(user=user)
    
    verification_codes = {
        'Withdrawal OTP': user.withdrawal_otp,
        'Tax Verification': user.tax_verification_code,
        'Identity Verification': user.identity_verification_code,
        'Final Verification': user.final_verification_code
    }
    
    account_details = {
        'Account Number': user.account_number,
        'Bank Name': user.bank_name,
        'Account Name': user.account_name,
        'Phone Number': user.phone_number,
        'Balance': user.balance,
        'Withdrawal Amount': user.withdrawal_amount
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            step = request.POST.get('step')
            setattr(verification_status, f'{step}_verified', True)
            verification_status.save()
            
            # Update user verification progress
            verified_steps = sum(1 for field in ['withdrawal_verified', 'tax_verified', 
                                               'identity_verified', 'final_verified'] 
                               if getattr(verification_status, field))
            user.verification_progress = (verified_steps / 4) * 100
            
            if verified_steps == 4:
                user.is_verified = True
            
            user.save()

            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action='verify',
                target_user=user,
                description=f'Verified {step} step',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'{step.title()} verification completed')
        
        elif action == 'update_details':
            # Update user details
            user.balance = request.POST.get('balance', user.balance)
            user.withdrawal_amount = request.POST.get('withdrawal_amount', user.withdrawal_amount)
            user.account_number = request.POST.get('account_number', user.account_number)
            user.bank_name = request.POST.get('bank_name', user.bank_name)
            user.account_name = request.POST.get('account_name', user.account_name)
            user.phone_number = request.POST.get('phone_number', user.phone_number)
            user.save()
            
            AdminLog.objects.create(
                admin=request.user,
                action='update',
                target_user=user,
                description='Updated user details',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'User details updated successfully')
            
    context = {
        'user': user,
        'verification_status': verification_status,
        'documents': documents,
        'verification_codes': verification_codes,
        'account_details': account_details,
        'activity_log': AdminLog.objects.filter(target_user=user).order_by('-timestamp'),
        'verification_progress': user.verification_progress
    }
    
    return render(request, 'admin_portal/user_detail.html', context)


@staff_member_required
def document_review(request):
    pending_documents = Document.objects.filter(
        documentreview__status='pending'
    ).select_related('user')
    
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        document = get_object_or_404(Document, id=document_id)
        review = DocumentReview.objects.get_or_create(document=document)[0]
        review.status = action
        review.review_notes = notes
        review.reviewer = request.user
        review.save()
        
        messages.success(request, f'Document {action}')
        
    context = {
        'pending_documents': pending_documents
    }
    return render(request, 'admin_portal/document_review.html', context)

@staff_member_required
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Update basic user information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        
        # Update financial details
        user.balance = request.POST.get('balance', user.balance)
        user.withdrawal_amount = request.POST.get('withdrawal_amount', user.withdrawal_amount)
        
        # Update account details
        user.account_name = request.POST.get('account_name')
        user.account_number = request.POST.get('account_number')
        user.phone_number = request.POST.get('phone_number')
        user.bank_name = request.POST.get('bank_name')
        
        # Update verification codes
        user.withdrawal_otp = request.POST.get('withdrawal_otp', user.withdrawal_otp)
        user.tax_verification_code = request.POST.get('tax_verification_code', user.tax_verification_code)
        user.identity_verification_code = request.POST.get('identity_verification_code', user.identity_verification_code)
        user.final_verification_code = request.POST.get('final_verification_code', user.final_verification_code)
        
        user.save()
        
        # Log the update action
        AdminLog.objects.create(
            admin=request.user,
            action='update',
            target_user=user,
            description='Updated user details',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'User details updated successfully')
        return redirect('admin_portal:user_detail', user_id=user.id)
    
    return redirect('admin_portal:user_detail', user_id=user.id)




from django.contrib.auth import login
from django.contrib import messages

@staff_member_required
def login_as_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Store admin session data
    request.session['admin_id'] = request.user.id
    
    # Login as the target user
    login(request, user)
    
    # Log this action
    AdminLog.objects.create(
        admin_id=request.session['admin_id'],
        action='login_as_user',
        target_user=user,
        description=f'Admin logged in as user {user.email}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    messages.success(request, f'You are now logged in as {user.email}')
    return redirect('users:dashboard')  # Redirect to user dashboard


