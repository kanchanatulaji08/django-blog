from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("blog:post_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("blog:post_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # sign the new user in straight away
        messages.success(self.request, f"Welcome, {self.object.username}! Your account was created.")
        return response
