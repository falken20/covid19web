# by Richi Rod AKA @richionline / falken20

import os
import logging
from django.shortcuts import render
from django.db.models import Sum
from .models import DataCovid19Item


def resume_view(request):
    """ Showing a resume data table of a country that it indicates in the var country_name """

    print(request)
    if request.POST:
        country_name = request.POST['country_name']
    else:
        country_name = 'Spain'
    logging.info(f'{os.getenv("ID_LOG", "")} Showing the resume table for {country_name}')

    # Get the countries names for the combo to shoose country
    countries = DataCovid19Item.objects.values('country').order_by('country').distinct()

    # Get the last record in DB grouping by country_name and date, the view shows data from Spain by default
    # This is because the amount of the vars is accumulated every day
    queryset = DataCovid19Item.objects.values('country',
                                              'date').annotate(dead_cases=Sum('dead_cases'),
                                                               confirmed_cases=Sum('confirmed_cases'),
                                                               recovered_cases=Sum('recovered_cases'),
                                                               active_cases=Sum('active_cases'),
                                                               ).filter(country=country_name).order_by('-date')[0]

    # Calculate mortality and recovered tax
    queryset['mortality_tax'] = round(queryset['dead_cases'] / queryset['confirmed_cases'] * 100, 2)
    queryset['recovered_tax'] = round(queryset['recovered_cases'] / queryset['confirmed_cases'] * 100, 2)

    # Format the thousands and decimal separators
    # :,d means format thousands separators in a integer
    # :,.2f means format thousands and deciman separators in a float
    queryset['dead_cases'] = f'{queryset["dead_cases"]:,d}'
    queryset['confirmed_cases'] = f'{queryset["confirmed_cases"]:,d}'
    queryset['recovered_cases'] = f'{queryset["recovered_cases"]:,d}'
    queryset['active_cases'] = f'{queryset["active_cases"]:,d}'
    queryset['mortality_tax'] = f'{queryset["mortality_tax"]:,.2f}'
    queryset['recovered_tax'] = f'{queryset["recovered_tax"]:,.2f}'

    logging.info(f'{os.getenv("ID_LOG", "")} Getting the resume data for {country_name}: \n {queryset}')

    template_name = 'covid19data/resume.html'

    return render(request, template_name, {'resume_data': queryset, 'countries': countries})


def heatmap_view(request):
    """ For showing heat map."""

    logging.info(f'{os.getenv("ID_LOG", "")} Showing the heat map')
    template_name = 'covid19data/heat_map.html'

    return render(request, template_name)


def graph_view(request, graph_type='confirmed'):
    """
    Showing graphs about data
    :param request: Request
    :param graph_type: What type of graph to show: confirmed, recovered o deaths
    """
    logging.info(f'{os.getenv("ID_LOG", "")} Showing graph for {graph_type} cases')

    template_name = 'covid19data/graph.html'

    return render(request, template_name, {'graph_type': graph_type})
