from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.utils import timezone
from django.db import models

from .forms import LoginForm, StudentSignUpForm, EditProfileForm
from .login_tracker import LoginAttemptTracker
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Contact, Complaint, RoomBooking, Payment, Profile, Notice
from django.core.mail import send_mail  # ✅ added for email sending

# -------------------------------
# PDF Generation
# -------------------------------
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

# ================================
# Pages / Views
# ================================
def index(request):
    return render(request, 'index.html', {"variable": "This is the eg"})

def home(request):
    # Fetch only active notices (latest 3)
    latest_notices = Notice.objects.filter(is_active=True).order_by('-date_posted')[:3]
    return render(request, 'home.html', {'latest_notices': latest_notices})

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

# -------------------------------
# Contact View (with user autofill)
# -------------------------------
def contact(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            # Automatically link the contact with the logged-in user
            Contact.objects.create(
                user=request.user,
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                email=request.user.email,
                phone=request.POST.get('phone'),
                message=request.POST.get('message')
            )
        else:
            # For guest users
            Contact.objects.create(
                first_name=request.POST.get('firstname'),
                last_name=request.POST.get('lastname'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                message=request.POST.get('message')
            )

        messages.success(request, "Contact details submitted successfully.")
        return redirect('Home')

    # Prefill data for logged-in users
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'firstname': request.user.first_name,
            'lastname': request.user.last_name,
            'email': request.user.email,
        }

    return render(request, 'contact.html', {'initial_data': initial_data})


# -------------------------------
# Room Booking View
# -------------------------------
def room_booking(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            first_name = request.user.first_name
            last_name = request.user.last_name
            student_id = profile.student_id
            email = request.user.email
        else:
            full_name = request.POST.get('full_name', '')
            first_name, last_name = (full_name.split(' ', 1) + [""])[:2]
            student_id = request.POST.get('student_id', '')
            email = request.POST.get('email', '')

        RoomBooking.objects.create(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            email=email,
            room_type=request.POST.get('room_type', ''),
            check_in_date=request.POST.get('check_in_date', None),
            check_out_date=request.POST.get('check_out_date', None),
            additional_requests=request.POST.get('additional_requests', '')
        )
        messages.success(request, "Your room booking request has been submitted successfully.")
        return redirect('Home')

    initial_data = {}
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}",
            'student_id': profile.student_id,
            'email': request.user.email,
        }

    return render(request, 'room_booking.html', {'initial_data': initial_data})

# -------------------------------
# Complaint View (with Email Notification)
# -------------------------------
def complaints(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            student_id = profile.student_id
            name = f"{request.user.first_name} {request.user.last_name}"
            email = request.user.email
        else:
            student_id = request.POST.get('student_id')
            name = request.POST.get('name')
            email = request.POST.get('email')

        # Save complaint
        complaint = Complaint.objects.create(
            user=request.user if request.user.is_authenticated else None,
            student_id=student_id,
            name=name,
            email=email,
            complaint_type=request.POST.get('complaint_type'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority', 'medium')
        )

        # -------------------------------
        # Email Notification Section
        # -------------------------------
        try:
            admin_subject = f"🛎 New Complaint from {name}"
            admin_message = (
                f"A new complaint has been submitted.\n\n"
                f"Student ID: {student_id}\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Complaint Type: {complaint.complaint_type}\n"
                f"Priority: {complaint.priority}\n\n"
                f"Description:\n{complaint.description}\n\n"
                f"Submitted on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # send email to admin
            send_mail(
                subject=admin_subject,
                message=admin_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['your_admin_email@gmail.com'],  # 👈 change this to teacher email
                fail_silently=False,
            )

            # send confirmation email to student
            if email:
                user_subject = "✅ Complaint Submitted Successfully"
                user_message = (
                    f"Hello {name},\n\n"
                    f"Your complaint has been received successfully.\n"
                    f"Our team will review it shortly.\n\n"
                    f"Complaint Details:\n"
                    f"Type: {complaint.complaint_type}\n"
                    f"Priority: {complaint.priority}\n"
                    f"Description: {complaint.description}\n\n"
                    f"Thank you,\nHostel Management System"
                )
                send_mail(
                    subject=user_subject,
                    message=user_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )

            messages.success(request, "✅ Complaint submitted and email notification sent successfully!")

        except Exception as e:
            messages.warning(request, f"Complaint saved, but email could not be sent. Error: {e}")

        return redirect('Home')

    initial_data = {}
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        initial_data = {
            'student_id': profile.student_id,
            'name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email
        }

    return render(request, "complaints.html", {'initial_data': initial_data})

# -------------------------------
# Payment Management
# -------------------------------
def payment_management(request):
    status_filter = request.GET.get('status')
    payments = Payment.objects.all()
    if status_filter in ['completed', 'pending', 'failed', 'refunded']:
        payments = payments.filter(payment_status=status_filter)

    total_collected = Payment.objects.filter(payment_status='completed').aggregate(
        total_amount_sum=models.Sum('amount'))['total_amount_sum'] or 0
    total_pending = Payment.objects.filter(payment_status='pending').aggregate(
        total_amount_sum=models.Sum('amount'))['total_amount_sum'] or 0
    this_month = Payment.objects.filter(payment_date__month=timezone.now().month).aggregate(
        total_amount_sum=models.Sum('amount'))['total_amount_sum'] or 0
    total_payments = payments.count()

    initial_data = {}
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        initial_data = {
            'student_id': profile.student_id,
            'name': f"{request.user.first_name} {request.user.last_name}",
            'email': request.user.email
        }

    context = {
        'payments': payments,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'this_month': this_month,
        'total_payments': total_payments,
        'initial_data': initial_data
    }
    return render(request, 'payment_management.html', context)

# -------------------------------
# New Payment
# -------------------------------
def new_payment(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            student_id = profile.student_id
            name = f"{request.user.first_name} {request.user.last_name}"
            email = request.user.email
        else:
            student_id = request.POST.get('student_id')
            name = request.POST.get('name')
            email = request.POST.get('email')

        Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            student_id=student_id,
            name=name,
            email=email,
            amount=request.POST.get('amount'),
            payment_method=request.POST.get('payment_method'),
            notes=request.POST.get('notes'),
            payment_status='pending'
        )
        messages.success(request, "Payment recorded successfully!")

    return redirect('payment_management')

# -------------------------------
# Edit Payment
# -------------------------------
@login_required
def edit_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.payment_status != 'pending':
        messages.error(request, "Only pending payments can be edited.")
        return redirect('payment_management')

    if request.method == "POST":
        payment.amount = request.POST.get('amount', payment.amount)
        payment.payment_method = request.POST.get('payment_method', payment.payment_method)
        payment.notes = request.POST.get('notes', payment.notes)
        payment.save()
        messages.success(request, "Payment updated successfully!")
        return redirect('payment_management')

    return render(request, 'edit_payment.html', {'payment': payment})

# -------------------------------
# Delete Payment
# -------------------------------
@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.payment_status != 'pending':
        messages.error(request, "Only pending payments can be deleted.")
    else:
        payment.delete()
        messages.success(request, "Payment deleted successfully!")
    return redirect('payment_management')

# -------------------------------
# Download Receipt
# -------------------------------
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    template = get_template('receipt.html')
    html = template.render({'payment': payment})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response

# -------------------------------
# Signup / Login / Logout / Profile
# -------------------------------
def signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentSignUpForm()
    return render(request, 'signup.html', {'form': form})

@never_cache
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('Home')

    form = LoginForm(request.POST or None, request=request)
    if request.method == 'POST':
        email = form.data.get('email', '').strip().lower()
        client_ip = LoginAttemptTracker.get_client_ip(request)

        is_locked, remaining_seconds = LoginAttemptTracker.is_locked_out(email, client_ip)
        if is_locked:
            remaining_minutes = (remaining_seconds + 59) // 60
            messages.error(request, f"Too many failed login attempts. Try again in {remaining_minutes} minute(s).")
            return render(request, 'login.html', {'form': form})

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            remember_me = form.cleaned_data.get('remember_me', False)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE if remember_me else 0)
            LoginAttemptTracker.clear_attempts(email, client_ip)
            messages.success(request, "Login successful! Welcome back.")
            next_url = request.GET.get('next') or request.POST.get('next')
            return HttpResponseRedirect(next_url or '/')
        else:
            is_locked, _ = LoginAttemptTracker.record_failed_attempt(email, client_ip)
            remaining_attempts = LoginAttemptTracker.get_remaining_attempts(email, client_ip)
            if is_locked:
                messages.error(request, "Too many failed attempts. Your account is temporarily locked.")
            elif remaining_attempts <= 2:
                messages.warning(request, f"Invalid credentials. {remaining_attempts} attempt(s) remaining before lockout.")
            else:
                messages.error(request, "Invalid email or password. Please try again.")

    return render(request, 'login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return render(request, "logout.html")

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EditProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

# -------------------------------
# Help and Student Records
# -------------------------------
def help_page(request):
    return render(request, 'help.html')

def student_records(request):
    return render(request, 'student_records.html')

# -------------------------------
# Notice Board
# -------------------------------
def notice_board(request):
    notices = Notice.objects.filter(is_active=True).order_by('-date_posted')
    return render(request, 'notice_board.html', {'notices': notices})

