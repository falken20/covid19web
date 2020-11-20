"""
Cron to generate graphs and heat map from DB data for COVID19
"""

import logging
import os
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv, find_dotenv
from datetime import date
from dateutil.parser import parse
# Heat map and graphs
from matplotlib import pyplot as plt
import folium
import math
from folium.plugins import HeatMap

# If you’re using components of Django “standalone” – for example, writing a Python script which
# loads some Django components
# https://docs.djangoproject.com/en/3.1/topics/settings/#custom-default-settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'covid19web.settings')
import django
from django.db.models import Sum

django.setup()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_fk import SETUP_DATA
from app_covid19data.models import DataCovid19Item

PATH_MAP = '../templates/covid19data/'
PATH_GRAPH = '../static/covid19web/img/'

# Load env file
load_dotenv(find_dotenv())

# Set log level and secret key
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))


def generate_graph(_list_data, _label='Graph', _color='Pink'):
    """
    Method for generate the graph with the data
    :param _color: Color for the line in the graph
    :param _label: Label to show in the plot
    :param _list_data: List of data to show
    """

    logging.info(f'Start to generate the graph of {_label}')

    # Generate the graph
    x = [i for i in range(0, len(_list_data))]
    plt.style.use('seaborn-talk')
    plt.plot(x, _list_data, color=_color, label=_label, linewidth=1.0)
    plt.xlabel('Days')
    plt.ylabel('People number')
    plt.title(f'COVID-19 Evolution')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.savefig(f'{PATH_GRAPH}graph_{_color}.png')
    # plt.show()
    plt.close()

    print(f'Graph of {_label} generates successfully')


def generate_heat_map(_queryset):
    """
    Method to generate a heat map with all the values
    :param _queryset: List of values for every day
    """

    logging.info('Start to generate the heat map')

    try:
        heat_map = folium.Map(location=[43, 0],
                              zoom_start='3',
                              tiles='Stamen Toner',
                              width='99%',
                              height='99%')
        location = []

        for row in _queryset:
            if row['latitude'] is None or row['longitude'] is None or \
                    math.isnan(row['latitude']) or math.isnan(row['longitude']):
                pass
            else:
                location.append([row['latitude'], row['longitude']])

        HeatMap(location, radius=16).add_to(heat_map)
        heat_map.save(f'{PATH_MAP}heatMap.html')

        print('Heat map successfully generated in html')

    except Exception as err:
        logging.error(f'\nRow: {row}'
                      f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


def get_accumulate_amounts():
    """
    Return the accumulate amounts per day
    :return: Return a queryset
    """
    try:
        queryset = DataCovid19Item.objects.values('date').annotate(dead_cases=Sum('dead_cases'),
                                                                   confirmed_cases=Sum('confirmed_cases'),
                                                                   recovered_cases=Sum('recovered_cases'),
                                                                   active_cases=Sum('active_cases'),
                                                                   ).order_by('date')
        return queryset

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
    finally:
        print(f'Getting {len(queryset)} rows from the DB with accumulate amounts')


def get_location_coordinates():
    """
    Return all the location coordinates
    :return: Return a queryset
    """
    try:
        queryset = DataCovid19Item.objects.values('latitude', 'longitude')
        return queryset

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
    finally:
        print(f'Getting {len(queryset)} rows from the DB with location coordinates')


def cron_graph():
    """
    Method to generate graphs and heat map from DB data
    """
    try:
        queryset = get_accumulate_amounts()

        # From the queryset get a list with values for each type (dead, recovered, confirmed)
        generate_graph([queryset[row]['dead_cases'] for row in range(0, len(queryset))],
                       'Dead cases', 'red')
        generate_graph([queryset[row]['confirmed_cases'] for row in range(0, len(queryset))],
                       'Confirmed cases', 'black')
        generate_graph([queryset[row]['recovered_cases'] for row in range(0, len(queryset))],
                       'Recovered cases', 'blue')

        # Generate heat map
        queryset = get_location_coordinates()
        generate_heat_map(queryset)

    except Exception as err:
        logging.error(f'\nError at line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


# Create the cron object
cron_graphs = BlockingScheduler()


# Set up the cron as 'interval' and executing every 8 hours
@cron_graphs.scheduled_job('interval', hours=24, start_date='2020-11-21 05:15:00')
# @cron_graphs.scheduled_job('interval', seconds=20)
def timed_job():
    """ Method to schedule the cron """
    print(f'********* START CRON GRAPHS {SETUP_DATA["title"]} *********')
    cron_graph()
    print(f'********* END CRON GRAPHS {SETUP_DATA["title"]} *********')


cron_graphs.start()
