import json
import csv
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .data_engine import CrimeDataEngine


def dashboard(request):
    """Main dashboard view with pre-computed initial payload for instant rendering."""
    engine = CrimeDataEngine.get_instance()

    default_state = "Karnataka"
    default_year = "2022"

    initial_summary = engine.get_summary(state=default_state, year=default_year)
    initial_trends = engine.get_trends(state=default_state)
    initial_rankings = engine.get_district_rankings(state=default_state, year=default_year, limit=12)
    initial_categories = engine.get_category_breakdown(state=default_state, year=default_year)
    initial_table = engine.get_table_data(state=default_state, year=default_year, page=1, page_size=15)
    states_list = engine.get_states()

    context = {
        'default_state': default_state,
        'default_year': default_year,
        'states_list': states_list,
        'initial_summary_json': json.dumps(initial_summary),
        'initial_trends_json': json.dumps(initial_trends),
        'initial_rankings_json': json.dumps(initial_rankings),
        'initial_categories_json': json.dumps(initial_categories),
        'initial_table_json': json.dumps(initial_table),
        'states_list_json': json.dumps(states_list),
    }
    return render(request, "index.html", context)


def api_states(request):
    """Returns all 36 States/UTs and their respective districts."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state')
    return JsonResponse({
        'states': engine.get_states(),
        'districts': engine.get_districts(state)
    })


def api_summary(request):
    """Returns executive KPIs and YoY growth for selected state and year."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    year = request.GET.get('year', '2022')
    data = engine.get_summary(state=state, year=year)
    return JsonResponse(data)


def api_trends(request):
    """Returns 2016-2022 timeline trends for selected state and optional district."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    district = request.GET.get('district', None)
    data = engine.get_trends(state=state, district=district)
    return JsonResponse({'trends': data})


def api_districts(request):
    """Returns district rankings for bar charts and comparative analytics."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    year = request.GET.get('year', '2022')
    metric = request.GET.get('metric', 'total')
    try:
        limit = int(request.GET.get('limit', 15))
    except (ValueError, TypeError):
        limit = 15
    data = engine.get_district_rankings(state=state, year=year, metric=metric, limit=limit)
    return JsonResponse({'districts': data})


def api_categories(request):
    """Returns category breakdown and percentages."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    year = request.GET.get('year', '2022')
    district = request.GET.get('district', None)
    data = engine.get_category_breakdown(state=state, year=year, district=district)
    return JsonResponse(data)


def api_district_detail(request):
    """Returns deep-dive historical profile for a district."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    district = request.GET.get('district', 'Bengaluru Urban')
    data = engine.get_district_detail(state=state, district=district)
    return JsonResponse(data)


def api_table_data(request):
    """Returns filtered, sorted, paginated records for the data explorer table."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    year = request.GET.get('year', '2022')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'total')
    sort_order = request.GET.get('order', 'desc')
    try:
        page = int(request.GET.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = int(request.GET.get('page_size', 15))
    except (ValueError, TypeError):
        page_size = 15

    data = engine.get_table_data(
        state=state, year=year, search=search,
        sort_by=sort_by, sort_order=sort_order,
        page=page, page_size=page_size
    )
    return JsonResponse(data)


def api_export_csv(request):
    """Exports filtered crime records as a CSV file for download."""
    engine = CrimeDataEngine.get_instance()
    state = request.GET.get('state', 'Karnataka')
    year = request.GET.get('year', '2022')

    table_data = engine.get_table_data(state=state, year=year, page=1, page_size=5000)

    filename = f"KCAVP_{state.replace(' ', '_')}_{year}_crime_data.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'State', 'District', 'Year', 'Total IPC Crimes',
        'Violent Crimes', 'Women & Child Safety',
        'Property & Economic', 'Public Safety & Traffic',
        'Murder', 'Theft', 'Rape'
    ])

    for row in table_data['rows']:
        writer.writerow([
            row['state'], row['district'], row.get('year', year),
            row['total'], row['violent'], row['women_children'],
            row['property_economic'], row['public_safety'],
            row['murder'], row['theft'], row['rape']
        ])

    return response