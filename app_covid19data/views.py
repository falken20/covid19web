# by Richi Rod AKA @richionline / falken20

import os
import logging
from django.shortcuts import render
from django.db.models import Sum, Max
from .models import DataCovid19Item


def get_resume_country(_country_name):
    """
    Get the resume data for a country
    :param _country_name: Country name
    :return: Return a queryset with the data
    """
    try:
        logging.info(f'{os.getenv("ID_LOG", "")} Getting resume for {_country_name}')
        if _country_name.upper() == 'GLOBAL':
            queryset = \
                DataCovid19Item.objects.values('date').annotate(dead_cases=Sum('dead_cases'),
                                                                confirmed_cases=Sum('confirmed_cases'),
                                                                recovered_cases=Sum('recovered_cases'),
                                                                active_cases=Sum('active_cases'),
                                                                ).order_by('-date')[0]
        else:
            queryset = \
                DataCovid19Item.objects.values('country',
                                               'date').annotate(dead_cases=Sum('dead_cases'),
                                                                confirmed_cases=Sum('confirmed_cases'),
                                                                recovered_cases=Sum('recovered_cases'),
                                                                active_cases=Sum('active_cases'),
                                                                ).filter(country=_country_name).order_by('-date')[0]

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

        logging.info(f'{os.getenv("ID_LOG", "")} Resume for {_country_name} successfully')

        return queryset

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


def resume_view(request):
    """ Showing a resume data table of a country that it indicates in the var country_name """

    if request.POST:
        country_name = request.POST['country_name']
    else:
        country_name = 'Spain'
    logging.info(f'{os.getenv("ID_LOG", "")} Showing the resume table for {country_name}')

    # Get the countries names for the combo to shoose country
    countries = DataCovid19Item.objects.values('country').order_by('country').distinct()

    # Get the last record in DB grouping by country_name and date, the view shows data from Spain by default
    # This is because the amount of the vars is accumulated every day
    queryset = get_resume_country(country_name)

    queryset_global = get_resume_country('Global')

    template_name = 'covid19data/resume.html'

    return render(request, template_name, {'resume_country': queryset, 'resume_global': queryset_global,
                                           'countries': countries})


def get_detail_country(_country_name):
    """
    Get the detail for a country
    :param _country_name: Country name
    :return: Return a queryset with the data
    """
    try:
        logging.info(f'{os.getenv("ID_LOG", "")} Getting detail for {_country_name}')

        # Get the last data date
        query_max_date = DataCovid19Item.objects.filter(country=_country_name).aggregate(max_date=Max('date'))
        logging.info(f'{os.getenv("ID_LOG", "")} Max date for {_country_name} in DB: {query_max_date["max_date"]}')

        queryset = \
            DataCovid19Item.objects.values('country',
                                           'state',
                                           'date').annotate(dead_cases=Sum('dead_cases'),
                                                            confirmed_cases=Sum('confirmed_cases'),
                                                            recovered_cases=Sum('recovered_cases'),
                                                            active_cases=Sum('active_cases'),
                                                            ).filter(country=_country_name,
                                                                     date=query_max_date["max_date"],
                                                                     ).exclude(state='Unknown')

        for row in queryset:
            # Calculate mortality and recovered tax
            if row['dead_cases'] != 0:
                row['mortality_tax'] = round(row['dead_cases'] / row['confirmed_cases'] * 100, 2)
                row['mortality_tax'] = f'{row["mortality_tax"]:,.2f}'
            if row['recovered_cases'] != 0:
                row['recovered_tax'] = round(row['recovered_cases'] / row['confirmed_cases'] * 100, 2)
                row['recovered_tax'] = f'{row["recovered_tax"]:,.2f}'

            # Format the thousands and decimal separators
            # :,d means format thousands separators in a integer
            # :,.2f means format thousands and deciman separators in a float
            row['dead_cases'] = f'{row["dead_cases"]:,d}'
            row['confirmed_cases'] = f'{row["confirmed_cases"]:,d}'
            row['recovered_cases'] = f'{row["recovered_cases"]:,d}'
            row['active_cases'] = f'{row["active_cases"]:,d}'

        logging.info(f'{os.getenv("ID_LOG", "")} Get detail for {_country_name} successfully: {len(queryset)} rows')

        return queryset, query_max_date['max_date']

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


def detail_view(request, country='Spain'):
    """ Showing a detail data table of a country that it indicates in the param country """

    country = country.title()
    logging.info(f'{os.getenv("ID_LOG", "")} Showing the resume table for {country}')

    queryset, max_date = get_detail_country(country)
    template_name = 'covid19data/detail.html'

    return render(request, template_name, {'detail_country': queryset, 'country': country, 'max_date': max_date})


def get_global_rank():
    """ Get the country list order by mortality tax"""
    try:
        logging.info(f'{os.getenv("ID_LOG", "")} Getting the country list order by mortality tax')

        # Get the last data date
        query_max_date = DataCovid19Item.objects.aggregate(max_date=Max('date'))
        logging.info(f'{os.getenv("ID_LOG", "")} Max date in DB: {query_max_date["max_date"]}')

        queryset = \
            DataCovid19Item.objects.values('country',
                                           'date').annotate(dead_cases=Sum('dead_cases'),
                                                            confirmed_cases=Sum('confirmed_cases'),
                                                            recovered_cases=Sum('recovered_cases'),
                                                            active_cases=Sum('active_cases'),
                                                            ).filter(date=query_max_date["max_date"],
                                                                     ).order_by('-dead_cases')

        for row in queryset:
            # Calculate mortality and recovered tax
            if row['dead_cases'] != 0:
                row['mortality_tax'] = round(row['dead_cases'] / row['confirmed_cases'] * 100, 2)
                row['mortality_tax'] = f'{row["mortality_tax"]:,.2f}'
            if row['recovered_cases'] != 0:
                row['recovered_tax'] = round(row['recovered_cases'] / row['confirmed_cases'] * 100, 2)
                row['recovered_tax'] = f'{row["recovered_tax"]:,.2f}'

            # Format the thousands and decimal separators
            # :,d means format thousands separators in a integer
            # :,.2f means format thousands and deciman separators in a float
            row['dead_cases'] = f'{row["dead_cases"]:,d}'
            row['confirmed_cases'] = f'{row["confirmed_cases"]:,d}'
            row['recovered_cases'] = f'{row["recovered_cases"]:,d}'
            row['active_cases'] = f'{row["active_cases"]:,d}'

        logging.info(f'{os.getenv("ID_LOG", "")} Getting global rank successfully')

        return queryset, query_max_date["max_date"]

    except Exception as err:
        logging.error(f'\nLine: {err.__traceback__.tb_lineno} \n'
                      f'File: {err.__traceback__.tb_frame.f_code.co_filename} \n'
                      f'Type Error: {type(err).__name__} \n'
                      f'Arguments:\n {err.args}')


def global_view(request):
    """ Showing global country rank """
    logging.info(f'{os.getenv("ID_LOG", "")} Showing the global country rank')

    queryset, max_date = get_global_rank()
    template_name = 'covid19data/global.html'

    return render(request, template_name, {'global_rank': queryset, 'max_date': max_date})


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
