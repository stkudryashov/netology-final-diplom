from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import User, Product, ProductInfo

import random
import string


class AccountsTests(APITestCase):
    def test_create_account(self):
        url = '/api/v1/user/register'

        before_count = User.objects.count()

        email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '@test.com'
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': email,
            'password': password
        }
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), before_count + 1)


class ProductsTests(APITestCase):
    def test_category_list(self):
        url = '/api/v1/catalog/categories'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_shop_list(self):
        url = '/api/v1/catalog/categories'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
