from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import (BotUser)


# Create your tests here.

class TCase(APITestCase):
    URL = reverse('start')

    def test_start_bot(self):
        response = self.client.post(self.URL, data={
            'message': {
                'chat': {
                    'id': 1,
                },
                'username': 'TestUser'
            }
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(BotUser.objects.exists())
