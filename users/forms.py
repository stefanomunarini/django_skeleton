from allauth.socialaccount.models import SocialAccount
from django import forms
from django.contrib.auth.models import User
from django.forms import (
    ModelForm, )
from django.utils.translation import ugettext_lazy as _

from users.models import UserProfile


class AbstractSignupUserForm(ModelForm):
    email = forms.EmailField()
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification.")
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _('The passwords do not match.'),
                code='password_mismatch',
            )
        return password2

    def clean_email(self):
        username = self.cleaned_data.get('email')
        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError(_('This username is already in use.'))
        return username

    def save(self, *args, **kwargs):
        # if type(self) is SignupForm:
        #     group = Group.objects.get(pk=1)
        # elif type(self) is SignupForm:
        #     group = Group.objects.get(pk=2)
        # else:
        #     raise NotImplementedError()

        """
        Create the user to be linked to the UserProfile model
        """
        email = self.cleaned_data['email']
        user = User.objects.create_user(
            username=email,
            password=self.cleaned_data['password1'],
            email=email
        )
        # user.groups.set([group])
        user.is_active = False
        user.save()

        # context = Context({'user_id': user.id, 'username': user.username, 'url': 'https://' + HEROKU_HOST})
        # send_email(REGISTRATION_EMAIL_SUBJECT, 'auth/registration_email.html', [email], context)
        self.instance.user = user
        self.instance.user_id = user.id
        return super(AbstractSignupUserForm, self).save(*args, **kwargs)


class SignupForm(AbstractSignupUserForm):
    field_order = ('email', 'password1', 'password2')

    class Meta:
        model = UserProfile
        fields = ('display_name', 'profile_picture')


class UserUpdateModelForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        if not User.objects.filter(username=self.cleaned_data.get('email')).count() > 0:
            self.instance.username = self.instance.email
        return self.instance


class UserProfileUpdateModelForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('deactivated_until', 'user', 'third_party_login')

    def clean_display_name(self):
        if UserProfile.objects.filter(display_name=self.cleaned_data.get('display_name')).exclude(id=self.instance.id).count() > 0:
            self.add_error('display_name', _('The display name you chose is already taken.'))
        return self.cleaned_data.get('display_name')


class SignupSocialForm(forms.Form):

    def signup(self, request, user):
        # group_id = self.cleaned_data['group']
        # group = Group.objects.get(pk=group_id)
        # user.groups.set([group])
        user.save()

        social_profile = SocialAccount.objects.get(user_id=user.id)
        UserProfile.objects.create(
            user=user,
            display_name=self.cleaned_data['username'],
            third_party_login=social_profile.provider
        )