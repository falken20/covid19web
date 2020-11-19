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


def generate_heat_map(_list_data):
    """
    Method to generate a heat map with all the values
    :param _list_data: List of values for every day
    """

    logging.info('Start to generate the heat map')

    try:
        heat_map = folium.Map(location=[43, 0],
                              zoom_start='3',
                              tiles='Stamen Toner',
                              width='99%',
                              height='99%')
        location = []

        for c in range(0, len(_list_data)):
            for lat, lon in zip(_list_data[c]['Latitude'], _list_data[c]['Longitude']):
                if math.isnan(lat) or math.isnan(lon):
                    pass
                else:
                    location.append([lat, lon])

        HeatMap(location, radius=16).add_to(heat_map)
        heat_map.save(f'{PATH_MAP}heatMap.html')

        logging.info('Heat map successfully generated in html')

    except Exception as err:
        logging.error(f'\n_list_data: {_list_data[c]}'
                      f'Line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


def cron_covid19():
    """
    Method in which start the process and call the rest of the methods for calculating and get
    the data to save in DB
    """
    try:
        # Verify if we have to reloading data of several dates or loading only one day
        reload = True if os.getenv('RELOAD', 'N').upper() == 'Y' else False

        year = os.getenv('YEAR_FROM', 2020) if reload else date.today().year
        month = os.getenv('MONTH_FROM', 3) if reload else date.today().month
        day = os.getenv('DAY_FROM', 2020) if reload else date.today().day - 1

        list_urls = []
        # If environment var RELOAD is True load all the data from YEAR_FROM and MONTH_FROM
        if reload:
            list_urls = create_list_urls(year, month)
        else:
            list_urls = create_list_urls_day(year, month, day)

        # Deleting old data from the date before loading
        delete_data(year, month, day)

        # Transform the urls in a dataframe and after that in a list
        list_data = load_data_urls(list_urls)

        # Rename some columns names
        list_data = check_list(list_data)

        # Get different lists for every kind of data, dead, confirmed cases and recovered cases
        dead_cases, confirmed_cases, recovered_cases = generate_data_lists(list_data)

        # Create the graphs
        graphs = True
        if graphs:
            generate_graph(dead_cases, 'Dead cases', 'red')
            generate_graph(confirmed_cases, 'Confirmed cases', 'black')
            generate_graph(recovered_cases, 'Recovered cases', 'blue')

        # Generate summary table
        resume_data = \
            {'Dead cases': dead_cases[len(dead_cases) - 1],
             'Confirmed cases': confirmed_cases[len(confirmed_cases) - 1],
             'Recovered cases': recovered_cases[len(recovered_cases) - 1],
             'Mortality tax':
                 round(dead_cases[len(dead_cases) - 1] / confirmed_cases[len(confirmed_cases) - 1] * 100, 2),
             'Recovered tax':
                 round(recovered_cases[len(recovered_cases) - 1] / confirmed_cases[len(confirmed_cases) - 1] * 100, 2)
             }

        resume_data = pd.DataFrame(data=resume_data, index=[0])
        logging.info(f'Summary table: \n {resume_data}')

        # Generate heat map
        generate_heat_map(list_data)

    except Exception as err:
        logging.error(f'\nError at line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


if __name__ == '__main__':
    cron_covid19()

"""
# Create the cron object
cron_covid19 = BlockingScheduler()


# Set up the cron as 'interval' and executing every 8 hours
# @cron_covid19.scheduled_job('interval', hours=24, start_date='2020-11-01 23:45:00')
@cron_covid19.scheduled_job('interval', seconds=20)
def timed_job():
    print(f'********* START CRON {SETUP_DATA["title"]} *********')
    cron_covid19()
    print.info(f'********* END CRON {SETUP_DATA["title"]} *********')


cron_covid19.start()
"""