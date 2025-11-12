from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import Profile  # ✅ Import Profile model


# --------------------------
# 1. Signup Form
# --------------------------
class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    student_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    college = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'College / School'})
    )
    year = forms.ChoiceField(
        choices=[('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'student_id',
            'phone', 'college', 'year', 'password1', 'password2'
        )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
            # ✅ Create or update Profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.student_id = self.cleaned_data['student_id']
            profile.phone = self.cleaned_data['phone']
            profile.save()
        return user


# --------------------------
# 2. Email-only Login Form
# --------------------------
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'autocomplete': 'username',
            'required': True,
        }),
        label='Email'
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
            'required': True,
        }),
        label='Password'
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Remember me'
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            return cleaned_data

        try:
            user = User.objects.get(email=email.lower())
            username = user.username
        except User.DoesNotExist:
            raise ValidationError("No account found with this email.")

        user = authenticate(request=self.request, username=username, password=password)

        if user is None:
            raise ValidationError("Invalid email or password.")
        if not user.is_active:
            raise ValidationError("Your account is inactive. Please contact the administrator.")

        self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


# --------------------------
# 3. Edit Profile Form
# --------------------------
class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    student_id = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID'})
    )
    phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # ✅ Update Profile details
            profile, created = Profile.objects.get_or_create(user=user)
            profile.student_id = self.cleaned_data.get('student_id')
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        return user
    