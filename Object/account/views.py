import re

from .forms import EmailChangeForm
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views import View


# Create your views here.
def homepage(request):
    return render(request, "index/homepage.html")


def blogs(request):
    return render(request, "index/blogs.html")


def register(request):
    # Redirect authenticated users to homepage
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        password2 = request.POST.get("password2", "").strip()

        # Validate all inputs
        error_message = None
        if not all([first_name, last_name, username, email, password, password2]):
            error_message = "All fields are required."
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            error_message = (
                "Username can only contain letters, numbers, and underscores."
            )
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            error_message = "Invalid email format."
        elif (
            len(password) < 4
            or not re.search(r"\d", password)
            or not re.search(r"[A-Za-z]", password)
        ):
            error_message = "Password must be at least 8 characters long and include both letters and numbers."
        elif password != password2:
            error_message = "Passwords do not match."
        elif (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            error_message = "User with this username or email already exists."

        if error_message:
            messages.error(request, error_message)
            return redirect("register")

        # If no errors, proceed with user creation
        try:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=make_password(password),
            )
            user.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
        except Exception:
            messages.error(request, "Something went wrong. Please try again later.")
            return redirect("register")

    return render(request, "account/register.html")


class Login(View):
    @staticmethod
    def get(request):
        if request.user.is_authenticated:
            return redirect("homepage")
        form = AuthenticationForm()
        return render(request, "account/login.html", {"form": form})

    @staticmethod
    def post(request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session["user_id"] = user.id
            messages.success(request, "You are now logged in!")
            next_url = request.POST.get("next", "homepage")
            return redirect(next_url)
        messages.error(request, "Invalid username or password.")
        return render(request, "account/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("login")
    return redirect("homepage")


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")
        return email


@login_required
def user_details(request):
    """Handles user password and email updates securely."""
    user = request.user
    password_form = PasswordChangeForm(user)
    email_form = EmailChangeForm(instance=user)
    active_tab = "profile"  # Default tab

    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            active_tab = "password"
            if password_form.is_valid():
                user = password_form.save(commit=False)
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save(update_fields=["password"])
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated!")
                logout(request)
                return redirect("login")
            messages.error(request, "Please correct the errors below.")

        elif "change_email" in request.POST:
            email_form = EmailChangeForm(request.POST, instance=user)
            if email_form.is_valid():
                new_email = email_form.cleaned_data["email"].strip()
                user.refresh_from_db()
                if new_email and new_email != user.email:
                    user.email = new_email
                    user.save(update_fields=["email"])
                    messages.success(request, "Your email was successfully updated!")
                    return redirect("user_details")
                messages.info(request, "No changes were made to your email.")
            messages.error(request, "Please correct the errors below.")

    context = {
        "user": user,
        "password_form": password_form,
        "email_form": email_form,
        "active_tab": active_tab,
    }
    return render(request, "account/user_details.html", context)
