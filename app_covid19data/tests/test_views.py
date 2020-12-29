from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from app_covid19data.models import DataCovid19Item
from app_covid19data import views


class Covid19dataTest(TestCase):

    # Views tests
    def test_covid19data_resume_view(self):
        # First create several rows
        w = baker.make(DataCovid19Item, country='Spain', date=timezone.now().date(),
                       dead_cases=1, confirmed_cases=1, recovered_cases=1,
                       _quantity=5)
        url = reverse(views.resume_view)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # self.assertIn(w.title, resp.content)
