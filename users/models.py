from __future__ import unicode_literals

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):

    # Extend django.contrib.auth.models.user
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    # Natural language name for the player or the developer, e.g. ‘John Doe’, ‘ZombieSlayer99’ or ‘Samurai Games’
    display_name = models.CharField(_('Name'), max_length=50, unique=True)
    # A profile picture for the user or a logo for the developer
    profile_picture = CloudinaryField(
        _('Profile picture'), null=True, blank=True,
    )
    # End date for limited time bans
    deactivated_until = models.DateTimeField(null=True, blank=True)
    # A field to tie a 3rd party service to this user
    third_party_login = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.display_name
