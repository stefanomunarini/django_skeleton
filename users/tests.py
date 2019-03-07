# Create your tests here.

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse_lazy


class UserTest(TestCase):
    fixtures = ['groups.json', 'test_user.json']

    def setUp(self):
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
        users = User.objects.all()  # a, s, q, w
        self.userA = users[0]  # player
        self.userS = users[1]  # player
        self.userQ = users[2]  # developer
        self.userW = users[3]  # developer

        self.playerA_client = Client()
        self.playerA_client.login(username=self.userA.username, password='test')

        self.devQ_client = Client()
        self.devQ_client.login(username=self.userQ.username, password='test')

    def test_update_own_profile(self):
        url = reverse_lazy('profile:user-profile-update')

        response = self.devQ_client.get(url)
        self.assertContains(response, '<a href="/profile/">q@mail.com</a>')

        response = self.playerA_client.get(url)
        self.assertContains(response, '<a href="/profile/">a@mail.com</a>')

        data = {
            'display_name': 'Phu',
        }
        response = self.devQ_client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/profile/")
        updated_user = User.objects.filter(pk=self.userQ.id)[0]
        self.assertEqual(updated_user.profile.display_name, "Phu")
