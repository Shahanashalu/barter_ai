from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile
from django.contrib.auth.decorators import login_required

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']

        phone = request.POST.get('phonenumber')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        # Remove joined because profile does not have "joined" field
        # joined = request.POST.get('joined')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Create Profile with extra data
        Profile.objects.create(
            user=user,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode
        )

        messages.success(request, "Account created. Please login.")
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # home page
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    # Get or create user profile if it doesn’t exist
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    user = request.user

    if request.method == "POST":
        new_username = request.POST.get("username")

        # Check if username already exists
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "Username already taken!")
            return redirect("edit_profile")

        # Update username
        user.username = new_username
        user.save()

        # Update profile fields
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")
        profile.city = request.POST.get("city")
        profile.pincode = request.POST.get("pincode")
        profile.save()

        messages.success(request, "Your profile has been updated!")
        return redirect("profile")

    return render(request, "accounts/edit_profile.html", {"profile": profile})
