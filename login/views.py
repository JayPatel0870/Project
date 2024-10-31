from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('bill')  # Redirect to the 'bill' view
        else:
            return render(request, 'login/login.html', {'error': 'Invalid credentials'})
    return render(request, 'login/login.html')


@never_cache
@login_required
def home_view(request):
    return render(request, 'login/home.html')


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'login/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
