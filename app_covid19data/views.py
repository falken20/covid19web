# by Richi Rod AKA @richionline / falken20

import os
import logging
from django.shortcuts import render


def map_view(request):
    """ For showing heat map."""

    logging.info(f'{os.getenv("ID_LOG", "")} Showing the heat map')
    return render(request, 'covid19data/map.html')


def heatmap_view(request):
    """ For showing heat map."""

    logging.info(f'{os.getenv("ID_LOG", "")} Showing the heat map')
    return render(request, 'map/heatMap.html')

