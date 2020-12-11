from django.test import TestCase
from django.utils import timezone

from app_covid19data.models import DataCovid19Item

# Create your tests here.

# Model tests

class DataCovid19ItemTest(TestCase):

	def create_DataCovid19Item(self, country='countryTest', state='stateTest', latitude='1', longitude='1'):
		return DataCovid19Item.objects.create(country=country, state=state, latitude=latitude, 
                                              longitude=longitude, date=timezone.now())

	def test_DataCovid19Item_creation(self):
		w = self.create_DataCovid19Item()
		self.assertTrue(isinstance(w, DataCovidItem))
		self.assertEqual(w, w.country)
