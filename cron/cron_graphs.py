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