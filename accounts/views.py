from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import StudentRegistrationForm


def is_agency_user(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "staff"
    )


def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("home")

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("agency_dashboard" if is_agency_user(user) else "dashboard")



        return render(
            request,
            "accounts/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "accounts/login.html"
    )


def logout_view(request):

    logout(request)

    return redirect("login")


def home_view(request):

    if is_agency_user(request.user):
        return redirect("agency_dashboard")

    return render(
        request,
        "home.html"
    )
