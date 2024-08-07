from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django_six import force_text
from accounts.forms import LoginForm, RegistrationForm, UserForm, ProfileForm, CustomPasswordResetForm
from accounts.models import Profile
from accounts.token import account_activation_token
from .utils import send_email
from django.contrib.auth.tokens import default_token_generator


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                storage = messages.get_messages(request)
                for _ in storage:
                    pass
                messages.success(request, f"Welcome {username}")
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                else:
                    return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('accounts/email-template.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = [form.cleaned_data.get('email')] # Mailjet wait a list
            if send_email(subject=mail_subject, body=message, to_email_list=to_email):
                messages.success(request, f"Registration Successful. An activation link has been sent to {form.cleaned_data.get('email')}")
                return HttpResponseRedirect(reverse('login'))
            else:
                user.delete()
                messages.error(request, 'Failed to send activation email. Please try again.')
                return HttpResponseRedirect(reverse('register'))
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())

    return render(request, 'accounts/register.html', {'form': form})

def activate_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully!')
        return HttpResponseRedirect(reverse('index'))
    else:
        messages.error(request, 'The activation link is invalid!')
        return render(request, 'accounts/activation_invalid.html')

@login_required()
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.WARNING, "Logout Successful")
    return HttpResponseRedirect(reverse("index"))

@login_required()
def create_profile_view(request):
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm()
    if Profile.objects.filter(user=request.user).exists():
        messages.add_message(request, messages.WARNING, "Profile already exists")
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        profile = ProfileForm(request.POST, request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        if profile.is_valid() and user_form.is_valid():
            profile = profile.save(commit=False)
            profile.user = request.user
            profile.save()
            user_form.save()
            storage = messages.get_messages(request)
            for _ in storage:
                pass
            messages.add_message(request, messages.SUCCESS, "Profile Created Succesfully")
            return HttpResponseRedirect(reverse('profile', args=[profile.user.username]))
        else:
            for error in user_form.errors.values():
                messages.error(request, error.as_text())
            for error in profile.errors.values():
                messages.error(request, error.as_text())

    return render(request, 'accounts/create-profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update session to prevent log out
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('password_change')
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'accounts/password-change-form.html', {'form': form})

def profile_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        if request.user.is_authenticated and username == request.user.username:
            return HttpResponseRedirect(reverse('create_profile'))
        else:
            messages.add_message(request, messages.WARNING, "Profile does not exist")
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'accounts/profile-view.html', {'profile': profile})

@login_required
def edit_profile_view(request, username):
    if not Profile.objects.filter(user__username=username).exists():
        messages.warning(request, "Profile does not exist")
        return HttpResponseRedirect(reverse('index'))
    if username != request.user.username:
        messages.add_message(request, messages.ERROR, "You are not allowed to edit this profile")
        return HttpResponseRedirect(reverse('profile', args=[username]))
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.WARNING, "Profile does not exist")
        return HttpResponseRedirect(reverse('create_profile'))

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = request.user
            if 'profile_photo' in request.FILES:
                profile.profile_picture = request.FILES.get('profile_photo')
            else:
                pass
            profile.save()
            messages.success(request, "Profile updated successfully")
            return HttpResponseRedirect(reverse('profile', args=[profile.user.username]))
        else:
            for error in user_form.errors.values():
                messages.error(request, error.as_text())
            for error in profile_form.errors.values():
                messages.error(request, error.as_text())
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit-profile.html', {
        'profile_form': profile_form,
        'user_form': user_form
    })

def password_reset_view(request):
    form = CustomPasswordResetForm()
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            current_site = get_current_site(request)
            user = User.objects.get(email=form.cleaned_data['email'])
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/email-reset-password.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = [form.cleaned_data['email']]
            if send_email(subject=mail_subject, body=message, to_email_list=to_email):
                messages.success(request, "Your password reset link has been sent successfully. Please check your email.")
                return HttpResponseRedirect(reverse('login'))
            else:
                messages.error(request, "Your password reset link is invalid. Please try again.")
        else:
            for error in form.errors.values():
                messages.error(request, error.as_text())
    return render(request, 'accounts/password-change-form.html', {'form': form})


def password_reset_confirm(request, uidb64=None, token=None):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password was successfully updated!")
                return HttpResponseRedirect(reverse('login'))
        else:
            form = SetPasswordForm(user=user)
    else:
        form = None

    return render(request, 'accounts/password-change-form.html', {'form': form})


# Create your views here.
