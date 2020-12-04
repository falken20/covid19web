# by Richi Rod AKA @richionline / falken20

__title__ = 'COVID19 Falken'
__version__ = '1.0.0'
__author__ = 'Falken'
__url_github__ = 'https://github.com/falken20/'
__url_twitter__ = 'https://twitter.com/richionline'
__url_linkedin__ = 'https://www.linkedin.com/in/richionline/'
__license__ = 'MIT License'
__copyright__ = '© 2020 by Richi Rod AKA @richionline / falken20'
__features__ = [
    'Data by country',
    'Several graphs',
    'Heat map',
]


SETUP_DATA = {
    'title': __title__,
    'version': __version__,
    'author': __author__,
    'url_github': __url_github__,
    'url_twitter': __url_twitter__,
    'url_linkedin': __url_linkedin__,
    'license': __license__,
    'copyrigth': __copyright__,
    'features': __features__,
}

# .env file
"""
SECRET_KEY=
ENV_PRO=N
LOG_LEVEL=INFO
ID_LOG=ROD->
SQLITE=N
ALLOWED_HOSTS=

URL_CSV_FILES=https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports
# If RELOAD is Y delete and load new data from DAY_FROM/MONTH_FROM/YEAR_FROM (not included)
# If RELOAD is N the cron only load the current day data
RELOAD=N
DAY_FROM=20
MONTH_FROM=11
YEAR_FROM=2020

# Heroku
DJANGO_SETTINGS_MODULE=covid19web.settings
"""