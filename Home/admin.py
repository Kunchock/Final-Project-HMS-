from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from Home.models import Contact, Complaint, RoomBooking, Payment, Notice  # 👈 added Notice

# ---------------------------
# Global Admin Branding
# ---------------------------
admin.site.site_header = "Hostel Management System"
admin.site.site_title = "HMS Admin"
admin.site.index_title = "Welcome to Hostel Management System Administration"

# ---------------------------
# Contact Admin
# ---------------------------
from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "subject", "created_at", "is_responded", "reply_link")
    list_filter = ("is_responded", "created_at", "subject")
    search_fields = ("first_name", "last_name", "email", "phone", "subject")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 25

    actions = ["mark_as_responded", "mark_as_unresponded"]

    # ---------------------------
    # Custom admin action buttons
    # ---------------------------
    def mark_as_responded(self, request, queryset):
        updated = queryset.update(is_responded=True)
        self.message_user(request, f"{updated} contacts marked as responded.")
    mark_as_responded.short_description = "Mark selected contacts as responded"

    def mark_as_unresponded(self, request, queryset):
        updated = queryset.update(is_responded=False)
        self.message_user(request, f"{updated} contacts marked as unresponded.")
    mark_as_unresponded.short_description = "Mark selected contacts as unresponded"

    # ---------------------------
    # Add "Reply" link in admin
    # ---------------------------
    def reply_link(self, obj):
        if obj.email:
            return format_html(
                '<a class="button" href="mailto:{}?subject=Re:%20{}">Reply</a>',
                obj.email,
                obj.subject or "Your Message"
            )
        return "-"
    reply_link.short_description = "Reply via Email"
    reply_link.allow_tags = True


# ---------------------------
# Complaint Admin
# ---------------------------
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "student_id", "complaint_type", "status", "priority", "created_at")
    list_filter = ("complaint_type", "status", "priority", "created_at")
    search_fields = ("name", "email", "description")
    readonly_fields = ("created_at", "updated_at", "resolved_at")
    ordering = ("-created_at",)
    list_per_page = 20

    actions = ["mark_as_resolved", "mark_as_in_progress"]

    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status="resolved", resolved_at=timezone.now())
        self.message_user(request, f"{updated} complaints marked as resolved.")
    mark_as_resolved.short_description = "Mark selected complaints as resolved"

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"{updated} complaints marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected complaints as in progress"

# ---------------------------
# RoomBooking Admin
# ---------------------------
@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "student_id", "email", "room_type", "check_in_date", "check_out_date", "booking_status", "payment_status", "created_at")
    list_filter = ("room_type", "booking_status", "payment_status", "check_in_date", "check_out_date")
    search_fields = ("full_name", "student_id", "email", "additional_requests")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 25
    date_hierarchy = "check_in_date"

    actions = ["confirm_booking", "cancel_booking"]

    def confirm_booking(self, request, queryset):
        updated = queryset.update(booking_status="confirmed")
        self.message_user(request, f"{updated} bookings confirmed.")
    confirm_booking.short_description = "Confirm selected bookings"

    def cancel_booking(self, request, queryset):
        updated = queryset.update(booking_status="cancelled")
        self.message_user(request, f"{updated} bookings cancelled.")
    cancel_booking.short_description = "Cancel selected bookings"

# ---------------------------
# Payment Admin
# ---------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "student_id", "amount", "payment_status", "payment_method", "payment_date")
    list_filter = ("payment_status", "payment_method", "payment_date")
    search_fields = ("student_id", "notes")
    readonly_fields = ("created_at", "updated_at", "payment_date")
    ordering = ("-payment_date",)
    list_per_page = 25
    date_hierarchy = "payment_date"

    actions = ["mark_as_completed", "mark_as_failed", "mark_as_refunded"]

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(payment_status="completed")
        self.message_user(request, f"{updated} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(payment_status="failed")
        self.message_user(request, f"{updated} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"

    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(payment_status="refunded")
        self.message_user(request, f"{updated} payments marked as refunded.")
    mark_as_refunded.short_description = "Mark selected payments as refunded"

# ---------------------------
# Notice Admin (NEW)
# ---------------------------
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "date_posted", "is_active")
    list_filter = ("is_active", "date_posted")
    search_fields = ("title", "message")
    ordering = ("-date_posted",)
    list_per_page = 20

    actions = ["activate_notices", "deactivate_notices"]

    def activate_notices(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} notices activated.")
    activate_notices.short_description = "Activate selected notices"

    def deactivate_notices(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} notices deactivated.")
    deactivate_notices.short_description = "Deactivate selected notices"
