from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

import healthcheck.views


class TestViews(TestCase):
    def test_healthcheck(self):
        url = reverse(healthcheck.views.healthcheck)
        c = Client()
        res = c.get(url, {})
        self.assertEqual(res.status_code, 200, "is healthy?")
