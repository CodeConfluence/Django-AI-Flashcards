from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, LoginView, LogoutView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from django.utils.text import slugify
from django.contrib.auth import logout
from .models import Profile
from .forms import FlashcardSetForm, FlashcardForm

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            return render(request, 'accounts/registration/register.html')

        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/registration/register.html')

        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/registration/register.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            send_mail(
                'Welcome to SocialBrain.ai',
                'Thank you for registering with SocialBrain.ai!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return redirect('home')
        except ValidationError as e:
            return render(request, 'accounts/registration/register.html')

    return render(request, 'accounts/registration/register.html')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, self.template_name)


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    def post(self, request):
        logout(request)
        print("User logged out successfully") 
        return redirect('home')


class CustomPasswordResetView(LoginRequiredMixin, PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password_reset/done/'


def home_view(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # User is authenticated, retrieve agents associated with the user
        flashcard_sets = Flashcard_Set.objects.filter(creator=request.user)
    else:
        # User is not authenticated, set agents to None or an empty list
        flashcard_sets = None

    context = {
        'flashcard_sets': flashcard_sets,
    }
    return render(request, 'flashcardApp/home.html', context)

@login_required
def profile_view(request):
    user = request.user
    flashcard_sets = Flashcard_Set.objects.filter(creator=request.user)
    context = {
        'username': user.username,
        'name': user.first_name,
        'flashcard_sets': flashcard_sets,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def account_update_view(request):
    if request.method == 'POST':
        user = request.user

        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(user=user)

        # Handle profile image upload or removal
        if 'remove_profile_picture' in request.POST:
            # Remove the profile picture
            if profile.image:
                profile.image.delete()
                profile.image = None
        elif 'profile_image' in request.FILES:
            profile.image = request.FILES['profile_image']
        
        profile.save()

        # Handle name and username updates
        new_name = request.POST.get('name')
        new_username = request.POST.get('username')
        if new_name and new_name != user.first_name:
            user.first_name = new_name
        if new_username and new_username != user.username:
            user.username = new_username
        
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        if current_password and new_password:
            if check_password(current_password, user.password):
                user.set_password(new_password)
                update_session_auth_hash(request, user)
            else:
                error_message = "Invalid Current Password!"
                context = {'error': error_message, 'name': user.first_name, 'username': user.username}
                return render(request, 'accounts/profile.html', context)

        user.save()
    return redirect('account_update_confirmation')

@login_required
def profile_image_upload(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        user = request.user
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
        user.profile.image = request.FILES['profile_image']
        user.profile.save()
    return redirect('profile')

def account_update_confirmation_view(request):
    return render(request, 'accounts/account_updated_confirmation.html')

@login_required
def account_delete_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('home')
    return render(request, 'accounts/account_delete_confirmation.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import google.generativeai as genai

genai.configure(api_key=config('API_KEY'))

@csrf_exempt
def generate_content_view(request):
   pass
   
@login_required
def flashcard_set_list_view(request): 
   pass

@login_required
def flashcard_set_detail_view(request): 
   pass

@login_required
def flashcard_set_selection_view(request): 
   pass

@login_required
def create_flashcard_set_view(request):
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            flashcard_set = form.save(commit=False)
            flashcard_set.creator = request.user
            flashcard_set.save()
            return redirect('flashcard_set_list')
    else:
        form = FlashcardSetForm()
    return render(request, 'flashcard_app/create_flashcard_set.html', {'form': form})

@login_required
def update_flashcard_set_view(request):
    pass

@login_required
def delete_flashcard_set_view(request):
   pass
