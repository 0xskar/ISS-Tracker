import requests
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UserCreationForm, UserRegisterForm, CustomAuthenticationForm, UserProfileForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import City, UserProfile
from opencage.geocoder import OpenCageGeocode
from datetime import datetime, timedelta


def get_lat_long(city_name, country_name):
    key = 'd1f2a3a44d2a4f11b11495a90cec6a2b'  # Replace with your own API key
    geocoder = OpenCageGeocode(key)
    query = f'{city_name}, {country_name}'
    results = geocoder.geocode(query)
    if results:
        return results[0]['geometry']['lat'], results[0]['geometry']['lng']
    else:
        return None


# Create your views here.
def index(request):
    # Make a GET request to the ISS tracker API
    response = requests.get('http://api.open-notify.org/iss-now.json')
    # Extract the latitude and longitude from the response
    data = response.json()
    iss_latitude = data['iss_position']['latitude']
    iss_longitude = data['iss_position']['longitude']

    user = request.user
    if user.is_authenticated and user.userprofile.city:
        user_latitude, user_longitude = get_lat_long(user.userprofile.city, user.userprofile.country)

        context = {
            'latitude': iss_latitude,
            'longitude': iss_longitude,
            'user_latitude': user_latitude,
            'user_longitude': user_longitude,
        }
    else:
        context = {
            'latitude': iss_latitude,
            'longitude': iss_longitude,
        }
    return render(request, 'home.html', context)


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.userprofile.name}.')
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Create a new user object but don't save it yet
            new_user = form.save(commit=False)
            # Set the password to the user's input
            new_user.set_password(form.cleaned_data['password1'])
            # Save the User object
            new_user.save()
            # Authenticate the user and log them in
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            # Redirect to the home page
            messages.success(request, 'Your account has been created.')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'signup.html', {'form': form})


# cities view for ajax request in signup form:
@csrf_exempt
@require_POST
def get_cities(request):
    country_id = request.POST.get('country_id')
    cities = City.objects.filter(country_id=country_id)
    city_list = [{'id': city.id, 'name': city.name} for city in cities]
    return JsonResponse({'cities': city_list})


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user.userprofile)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.set_password(form.cleaned_data['password'])
            user_profile.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('home')
    else:
        form = UserProfileForm(instance=user.userprofile)

    return render(request, 'profile.html', {'form': form})


def custom_logout_view(request):
    logout(request)
    # Flash a message to the user
    messages.add_message(request, messages.SUCCESS, "Thanks for tracking, please come again soon!")
    return redirect('home')
