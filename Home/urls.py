from django.contrib import admin
from django.urls import path
from Home import views
from django.contrib.auth import views as auth_views

# Admin customization
admin.site.site_header = "HMS Admin"
admin.site.site_title = "HMS Admin Portal"
admin.site.index_title = "Welcome to HMS Portal"

urlpatterns = [
    # Home & general pages
    path("", views.index, name='HMS'),
    path("home/", views.home, name='Home'),
    path('notices/', views.notice_board, name='notice_board'),  
    path("about/", views.about, name='About'),
    path("services/", views.services, name='Services'),
    path("contact/", views.contact, name='Contact'),
    path("help/", views.help_page, name='Help'),
    path("room_booking/", views.room_booking, name='room_booking'),
    path("student_records/", views.student_records, name='student_records'),
    path("complaints/", views.complaints, name='complaints'),
    path("payment_management/", views.payment_management, name='payment_management'),

    # New payment submission
    path("payment_management/new/", views.new_payment, name='new_payment'),

    # Edit & Delete pending payments
    path("payment_management/<int:payment_id>/edit/", views.edit_payment, name="edit_payment"),
    path("payment_management/<int:payment_id>/delete/", views.delete_payment, name="delete_payment"),

    # Download receipt
    path("payment_management/<int:payment_id>/receipt/", views.download_receipt, name='download_receipt'),

    # Auth – custom views
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Password Reset – built-in Django views
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
