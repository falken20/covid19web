from django.shortcuts import render
import logging
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_fk import SETUP_DATA


def about_view(request):
    """ View for showing the About form of the project """

    logging.info(f'{os.getenv("ID_LOG", "")} Showing the About form')

    template_name = 'covid19web/about.html'

    return render(request, template_name, {'about_data': SETUP_DATA})


