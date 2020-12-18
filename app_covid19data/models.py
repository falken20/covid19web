import math
import logging
from django.db import models
from django.utils.timezone import now


class DataCovid19Item(models.Model):
    """ Class to store the COVID data """
    # About localization
    country = models.TextField(max_length=100)
    state = models.TextField(max_length=100, null=True)
    date = models.DateField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # About data incomes
    confirmed_cases = models.IntegerField(null=True, blank=True)
    dead_cases = models.IntegerField(null=True, blank=True)
    recovered_cases = models.IntegerField(null=True, blank=True)
    active_cases = models.IntegerField(null=True, blank=True)
    incidence_rate = models.FloatField(null=True, blank=True)
    case_fatality_ratio = models.FloatField(null=True, blank=True)
    # About update date
    update_date = models.DateTimeField(default=now)

    def __str__(self):
        return f'Daily data from {self.country}/{self.state} at {self.date}' \
               f'Lat/Long: {self.latitude}/{self.longitude}' \
               f'\nConfirmed: {self.confirmed_cases}' \
               f'\nDeaths: {self.dead_cases}' \
               f'\nRecovered: {self.recovered_cases}' \
               f'\nActive: {self.active_cases}' \
               f'\nIncidence: {self.incidence_rate}' \
               f'\nFatality Ratio: {self.case_fatality_ratio}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            # Check if float fields has NaN value
            for field in self._meta.fields:
                type = field.get_internal_type()
                if type in ['FloatField', 'IntegerField']:
                    value = getattr(self, field.name)
                    if value is None or math.isnan(value) or value == 'nan':
                        setattr(self, field.name, None)

            super(DataCovid19Item, self).save()

        except Exception as err:
            logging.error(f'\nField: {field.name}={value}'
                          f'\n{self}'
                          f'\nLine: {err.__traceback__.tb_lineno} \n'
                          f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                          f'Type Error: {type(err).__name__} \n'
                          f'Arguments:\n {err.args}')


