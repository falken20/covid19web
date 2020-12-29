from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from app_covid19data.models import DataCovid19Item


class Covid19dataTest(TestCase):

    def create_DataCovid19Item(self, country='countryTest', state='stateTest', latitude=1, longitude=1):
        return DataCovid19Item.objects.create(country=country, state=state, latitude=latitude,
                                              longitude=longitude, date=timezone.now())

    def test_covid19data_creation(self):
        # w = self.create_DataCovid19Item()
        w = baker.make(DataCovid19Item)
        self.assertTrue(isinstance(w, DataCovid19Item))

        r = f'Daily data from {w.country}/{w.state} at {w.date}' \
            f'Lat/Long: {w.latitude}/{w.longitude}' \
            f'\nConfirmed: {w.confirmed_cases}' \
            f'\nDeaths: {w.dead_cases}' \
            f'\nRecovered: {w.recovered_cases}' \
            f'\nActive: {w.active_cases}' \
            f'\nIncidence: {w.incidence_rate}' \
            f'\nFatality Ratio: {w.case_fatality_ratio}'
        self.assertEqual(w.__str__(), r)

    def test_covid19data_exception(self):
        self.assertRaises(Exception, self.create_DataCovid19Item, latitude='1')

    def test_covid19data_save(self):
        # w = self.create_DataCovid19Item()
        w = baker.make(DataCovid19Item)
        w.latitude = '1'
        self.assertRaises(Exception, w.save)