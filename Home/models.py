from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------------------
# Common Timestamp Model
# ---------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ---------------------------
# Profile Model     
# ---------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Automatically create or update Profile when User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        last_profile = Profile.objects.order_by('-id').first()
        next_id = (last_profile.id if last_profile else 0) + 1
        profile.student_id = f"SID{next_id}"  # e.g., SID1, SID2, SID15
        profile.save()
    else:
        instance.profile.save()

# ---------------------------
# Contact Model
# ---------------------------
class Contact(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=122)
    last_name = models.CharField(max_length=122)
    email = models.EmailField(max_length=122)
    phone = models.CharField(max_length=10)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    is_responded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ---------------------------
# Complaint Model
# ---------------------------
COMPLAINT_CHOICES = [
    ("cleanliness", "Cleanliness"),
    ("repair", "Repair"),
    ("noise", "Noise"),
    ("other", "Other"),
]

COMPLAINT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("in_progress", "In Progress"),
    ("resolved", "Resolved"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

class Complaint(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=COMPLAINT_STATUS_CHOICES, default="pending")
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Complaint by {self.name} ({self.complaint_type})"

# ---------------------------
# Room Booking Model
# ---------------------------
BOOKING_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("confirmed", "Confirmed"),
    ("checked_in", "Checked In"),
    ("checked_out", "Checked Out"),
    ("cancelled", "Cancelled"),
]

PAYMENT_STATUS_CHOICES = [
    ("unpaid", "Unpaid"),
    ("paid", "Paid"),
    ("refunded", "Refunded"),
]

class RoomBooking(TimeStampedModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20)
    email = models.EmailField()
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    room_type = models.CharField(max_length=20)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    additional_requests = models.TextField(blank=True, null=True)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")

    def __str__(self):
        return f"{self.full_name} - {self.room_type} ({self.booking_status})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ---------------------------
# Payment Model
# ---------------------------
PAYMENT_METHOD_CHOICES = [
    ("upi", "UPI"),
    ("card", "Card"),
    ("cash", "Cash"),
]

PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("refunded", "Refunded"),
]

class Payment(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_gateway = models.CharField(max_length=50, blank=True, null=True)
    gateway_response = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student_id} - {self.amount} ({self.payment_status})"

# ---------------------------
# Notice Model (NEW)
# ---------------------------
class Notice(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
