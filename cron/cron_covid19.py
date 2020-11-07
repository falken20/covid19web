"""
Cron to process data for COVID19 around the world and save in DB
"""

import logging
import os
import sys
from urllib.error import HTTPError
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv, find_dotenv
from datetime import date
from dateutil.parser import parse
# Heat map
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

URL_CSV_FILES = os.getenv('URL_CSV_FILES')
COL_STATE = 'Province_State'
COL_COUNTRY = 'Country_Region'
COL_LAST_UPDATE = 'Last_Update'
COL_LATITUDE = 'Latitude'
COL_LONGITUDE = 'Longitude'
COL_CONFIRMED_CASES = 'Confirmed'
COL_DEAD_CASES = 'Deaths'
COL_RECOVERED_CASES = 'Recovered'
COL_ACTIVE_CASES = 'Active'
COL_INCIDENCE_RATE = 'Incidence_Rate'
COL_CASE_FATALITY_RATIO = 'Case-Facility_Ratio'

PATH_MAP = '../templates/map/'

# Load env file
load_dotenv(find_dotenv())

# Set log level and secret key
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))


def save_data(df):
    """ Method to save data of dataframe in DB """
    try:
        # Get the colimns names because not always has all the columns
        name_cols = [col for col in df.columns]
        # Go over the dataframe df and save every row
        for index, row in df.iterrows():
            item = DataCovid19Item(country=row[COL_COUNTRY],
                                   state=row[COL_STATE],
                                   latitude=row[COL_LATITUDE],
                                   longitude=row[COL_LONGITUDE],
                                   confirmed_cases=row[COL_CONFIRMED_CASES],
                                   dead_cases=row[COL_DEAD_CASES],
                                   recovered_cases=row[COL_RECOVERED_CASES],
                                   )
            # Parser the date
            item.date = parse(row[COL_LAST_UPDATE])

            # Some columns not always exists in the files
            item.active_cases = row[COL_ACTIVE_CASES] if 'Active' in name_cols else 0
            item.incidence_rate = row[COL_INCIDENCE_RATE] if 'Incidence_Rate' in name_cols else 0
            item.case_fatality_ratio = row[COL_CASE_FATALITY_RATIO] if 'Case-Facility_Ratio' in name_cols else 0

            item.save()

    except Exception as err:
        logging.error(f'\nIndex={index} \n'
                      f'Row:\n{row} \n'
                      f'Line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
        raise
    else:
        logging.debug(f'{os.getenv("ID_LOG")} Successfully saved the df block')


def create_list_urls(_year_to_process=2020, _month_from=3):
    """
    Load all the urls of daily data of a specific year and from a specific month
    :param _year_to_process: Year to load
    :param _month_from: From this month start to load data
    :return:
    """

    if _year_to_process is None or _year_to_process == '':
        _year_to_process = 2020
    if _month_from is None or _month_from == '':
        _month_from = 3
    logging.info(f'Load a list with the CSV file names, one per every day from {_year_to_process}/{_month_from}')

    _list_urls = []
    try:
        # Get the number of the day in the current month
        # day = int(str(date.today())[-2:])
        current_day = date.today().day
        current_month = date.today().month
        logging.info(f'Current month and day: {current_month} / {current_day}')

        if int(_month_from) > int(current_month):
            logging.error(f'The chosen month is later the current month')
            return _list_urls

        # Load links for every day in all the months of the year least the current month
        for month in range(int(_month_from), current_month):
            for day in range(1, 32):
                _list_urls.append(
                    str(URL_CSV_FILES + f'/{str(month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        # Add links for every day in the current month
        for day in range(1, current_day):
            _list_urls.append(
                str(URL_CSV_FILES + f'/{str(current_month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        logging.info(f'Number of urls of data files: {len(_list_urls)}')

        return _list_urls

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
        raise


def rename_columns_list(_list_data):
    """ Unify the column name in a list for some columns because at the beginning the name was different """
    logging.debug('Rename some column name in dataframe')
    try:
        for c in range(0, len(_list_data)):
            _list_data[c].rename(columns={'Province/State': 'Province_State'}, inplace=True)
            _list_data[c].rename(columns={'Country/Region': 'Country_Region'}, inplace=True)
            _list_data[c].rename(columns={'Lat': 'Latitude'}, inplace=True)
            _list_data[c].rename(columns={'Long_': 'Longitude'}, inplace=True)
            _list_data[c].rename(columns={'Last Update': 'Last_Update'}, inplace=True)
    except Exception as err:
        logging.error(f'\n_list_data={_list_data} \n'
                      f'Line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
        raise
    finally:
        return _list_data


def check_df(_df_data, clean_nan=False):
    """ Unify the column name in dataframe for some columns because at the
    beginning the name was different. If clean_nan the it changes NaN values with 0 """
    logging.debug('Rename some column name in dataframe')
    try:
        _df_data.rename(columns={'Province/State': 'Province_State'}, inplace=True)
        _df_data.rename(columns={'Country/Region': 'Country_Region'}, inplace=True)
        _df_data.rename(columns={'Lat': 'Latitude'}, inplace=True)
        _df_data.rename(columns={'Long_': 'Longitude'}, inplace=True)
        _df_data.rename(columns={'Last Update': 'Last_Update'}, inplace=True)

        # Change NaN values for 0
        if clean_nan:
            _df_data.fillna(0)

    except Exception as err:
        logging.error(f'\n_df_data={_df_data} \n'
                      f'Line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
        raise
    finally:
        return _df_data


def load_data_urls(_list_urls):
    """
    Load the data for every url list element
    :param _list_urls: List where every element is a url to a CSV file data source
    """

    logging.info(f'Start to get the data from urls')

    _list_data = []
    urls_count = 0
    lines_count_df = 0
    try:
        for url in _list_urls:
            try:
                df_data = pd.read_csv(url, error_bad_lines=False)
            except HTTPError:
                logging.error(f'File not found: {url}')

            # Review df with correct columns names and NaN values
            df_data = check_df(df_data, clean_nan=True)

            np.array(df_data)
            _list_data.append(df_data)

            save_data(df_data)

            lines_count_df += len(df_data)
            urls_count += 1
            if urls_count % 10 == 0:
                print(f'Processing URLs: {urls_count}/{len(_list_urls)}'
                      f', Total saved rows in DB: {lines_count_df}')

    except Exception as err:
        logging.error(f'\nVars: url={url} \n'
                      f'Line: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')
    finally:
        return _list_data


def generate_data_lists(_list_data):
    """
    Method for generate several lists for dead data, confirmed cases and recovered cases
    :param _list_data: Data table with dead cases, confirmed cases and recovered cases
    :return: Three lists with separated data
    """

    logging.info('Start to generate the different lists for dead, confirmed and recovered data')

    # Create the lists for the graphs
    _list_dead_cases = []
    _list_confirmed_cases = []
    _list_recovered_cases = []

    # Sum the number of cases in every day
    for i in range(0, len(_list_data)):
        _list_dead_cases.append((_list_data[i]['Deaths']).sum())
        _list_confirmed_cases.append((_list_data[i]['Confirmed']).sum())
        _list_recovered_cases.append((_list_data[i]['Recovered']).sum())

    return _list_dead_cases, _list_confirmed_cases, _list_recovered_cases


def generate_graph(_list_data, _label, _color):
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
    # plt.savefig('falken_graph.png')
    plt.show()


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
                              width='100%',
                              height='100%')
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
        year_to_process = 2020
        month_from = 11
        graphs = False

        # Create a list with the urls to a every data day
        list_urls = create_list_urls(year_to_process, month_from)

        # Transform the urls in a dataframe and after that in a list and filtering by Spain or Global
        list_data = load_data_urls(list_urls)

        # Rename some columns names
        list_data = rename_columns_list(list_data)

        # Get different lists for every kind of data, dead, confirmed cases and recovered cases
        dead_cases, confirmed_cases, recovered_cases = generate_data_lists(list_data)

        # Create the graphs
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