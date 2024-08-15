from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from . forms import UserRegisterForm, UserLoginForm, EditUserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_view
from django.urls import reverse_lazy
from .models import Relation, Profile

# Create your views here.

class UserRegisterView(View):
    form_class = UserRegisterForm
    template_name = "accounts/register.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form":form})
    

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd["username"], cd["email"], cd["password"])
            messages.success(request, 'your register successfully', 'success')
            return redirect('home:home')
        return render(request, self.template_name, {"form":form})
    

class UserLoginView(View):
    form_class = UserLoginForm
    template_name = "accounts/login.html"

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next")
        return super().setup(request, *args, **kwargs)


    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form":form})

    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["username"], password=cd["password"])
            if user is not None:
                login(request, user)
                messages.success(request, "you successfully login", "success")
                if self.next:
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, "username or password is wrong", "warning")
        return render(request, self.template_name, {"form":form})


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, "you logout successfully", "success")
        return redirect("home:home")
    

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        is_following = False
        user = User.objects.get(id=user_id)
        posts = user.posts.all()
        relation = Relation.objects.filter(from_user = request.user, to_user = user)
        if relation.exists():
            is_following = True
        return render(request, "accounts/profile.html", {"user":user, "posts":posts, "is_following":is_following})
    
   
class UserPasswordResetView(auth_view.PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    email_template_name = "accounts/password_reset_email.html"


class UserPasswordResetDoneView(auth_view.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class UserPasswordresetConfrimView(auth_view.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confrim.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class UserPasswordResetCompleteView(auth_view.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user = request.user, to_user = user)
        if relation.exists():
            messages.error(request, "you alredy follow this user", "error")
        else:
            Relation(from_user = request.user, to_user = user).save()
            messages.success(request, "you follow this user", "success")
        return redirect("accounts:user_profile", user.id)


class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user = request.user, to_user = user)
        if relation.exists():
            relation.delete()
            messages.success(request, 'you unfollow this user', 'success')
        else:
            messages.error(request, "you not following this user", "error")
        return redirect("accounts:user_profile", user.id)
    

class EditUserView(LoginRequiredMixin, View):
    form_class = EditUserProfile

    def get(self, request):
        form = self.form_class(instance=request.user.profile, initial={"email":request.user.email})
        return render(request, "accounts/edit_profile.html", {"form":form})
    

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.success(request, "profile edited successfuly", "success")
            return redirect("accounts:user_profile", request.user.id)