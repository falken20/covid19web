from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from app_covid19data.models import DataCovid19Item
from app_covid19data import views


class Covid19dataTest(TestCase):

    def setUp(self):
        """ Method which the testing framework will automatically call before every single test we run """
        # Create several rows
        self.datacovid19 = baker.make(DataCovid19Item, country='Spain', date=timezone.now().date(),
                                      dead_cases=1, confirmed_cases=1, recovered_cases=1,
                                      _quantity=5)

    # Views tests
    def test_covid19data_resume_view(self):
        url = reverse(views.resume_view)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # self.assertIn(w.title, resp.content)

    def test_covid19data_get_resume_country(self):
        # The data for the test are loading in above setUp function
        queryset = views.get_resume_country('Spain')
        self.assertEqual(queryset['country'], 'Spain')
