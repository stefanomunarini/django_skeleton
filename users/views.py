from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin

from users.forms import (
    UserUpdateModelForm, UserProfileUpdateModelForm, SignupForm)


# User Signup

class AbstractSignupView(FormView):
    """
    This acts as a generic SignupView that is used by SignupPlayerView and SignupDeveloperView
    """
    success_url = reverse_lazy('profile:user-profile')

    def get(self, request, *args, **kwargs):
        # Don’t allow signups if the user is already logged in
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('home'))
        return super(AbstractSignupView, self).get(self, request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super(AbstractSignupView, self).form_valid(self)


class SignupView(AbstractSignupView):
    form_class = SignupForm
    template_name = 'signup.html'


class UserProfileDetailView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'user_profile_detail.html'


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserUpdateModelForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('profile:user-profile')
    template_name = 'user_profile_update.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = self.get_form(self.form_class)
        user_profile_form = UserProfileUpdateModelForm(
            instance=self.get_object().profile
        )
        return self.render_to_response(self.get_context_data(user_form=user_form, user_profile_form=user_profile_form))

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = self.get_form(self.form_class)
        user_profile_form = UserProfileUpdateModelForm(
            request.POST,
            request.FILES,
            instance=self.object.profile
        )
        if user_form.is_valid():
            user_form.save(commit=False)
            if user_profile_form.is_valid():
                user_profile_form.save()
                user_form.save()
                return super(UserProfileUpdateView, self).form_valid(form=user_form)
        return render(request, self.template_name, {'user_form': user_form, 'user_profile_form': user_profile_form})


class SignupActivateView(SingleObjectMixin, RedirectView):
    model = User
    url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        self.get_object()
        return super(SignupActivateView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.obj = super(SignupActivateView, self).get_object(queryset)
        self.obj.is_active = True
        self.obj.save()
        return self.obj
