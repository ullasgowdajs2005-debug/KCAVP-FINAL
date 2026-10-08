import json
import csv
import time
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .data_engine import CrimeDataEngine
from .chatbot_engine import CrimeChatbotEngine


def add_no_cache_headers(response):
    """Enforces zero-cache headers so browsers never serve stale cached data or assets."""
    response["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


def resolve_district(raw_name, districts_list):
    """Fuzzy case-insensitive district resolver with graceful fallback."""
    if not raw_name:
        return "Bengaluru City" if "Bengaluru City" in districts_list else districts_list[0]
    cleaned = raw_name.strip().lower()
    for d in districts_list:
        if d.lower() == cleaned:
            return d
    for d in districts_list:
        if cleaned in d.lower():
            return d
    return "Bengaluru City" if "Bengaluru City" in districts_list else districts_list[0]


def dashboard(request):
    """Main Single-District Crime Intelligence dashboard view with multi-year support (2016-2022)."""
    engine = CrimeDataEngine.get_instance()

    districts_list = engine.get_districts()
    raw_district = request.GET.get('district') or request.GET.get('state')
    selected_district = resolve_district(raw_district, districts_list)

    selected_year = request.GET.get('year', 'all').strip()

    initial_summary = engine.get_district_summary(selected_district, year=selected_year)
    initial_offenses = engine.get_district_offenses(selected_district, year=selected_year, limit=12)
    initial_critical = engine.get_district_critical_offenses(selected_district, year=selected_year)
    initial_categories = engine.get_district_category_distribution(selected_district, year=selected_year)
    initial_table = engine.get_district_table(selected_district, year=selected_year)
    initial_trends = engine.get_district_multi_year_trend(selected_district)

    available_years = [
        {'id': 'all', 'label': 'All Years (2016–2022)'},
        {'id': '2022', 'label': '2022 Data'},
        {'id': '2021', 'label': '2021 Data'},
        {'id': '2020', 'label': '2020 Data'},
        {'id': '2019', 'label': '2019 Data'},
        {'id': '2018', 'label': '2018 Data'},
        {'id': '2017', 'label': '2017 Data'},
        {'id': '2016', 'label': '2016 Data'},
    ]

    context = {
        'default_district': selected_district,
        'districts_list': districts_list,
        'selected_year': selected_year,
        'available_years': available_years,
        'summary': initial_summary,
        'categories_list': initial_categories.get('categories', []),
        'table': initial_table,
        'trends': initial_trends,
        'timestamp': int(time.time()),
        'initial_summary_json': json.dumps(initial_summary),
        'initial_offenses_json': json.dumps(initial_offenses),
        'initial_critical_json': json.dumps(initial_critical),
        'initial_categories_json': json.dumps(initial_categories),
        'initial_table_json': json.dumps(initial_table),
        'initial_trends_json': json.dumps(initial_trends),
        'districts_list_json': json.dumps(districts_list),
        'years_list_json': json.dumps([y['id'] for y in available_years if y['id'] != 'all']),
    }
    response = render(request, "index.html", context)
    return add_no_cache_headers(response)


def api_districts_list(request):
    """Returns the list of all Karnataka districts/commissionerates and available years."""
    engine = CrimeDataEngine.get_instance()
    response = JsonResponse({
        'state': 'Karnataka',
        'states': ['Karnataka'],
        'districts': engine.get_districts(),
        'years': engine.get_years()
    })
    return add_no_cache_headers(response)


def api_summary(request):
    """Returns executive KPIs and category breakdown for a single district and year."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    data = engine.get_district_summary(district=district, year=year)
    return add_no_cache_headers(JsonResponse(data))


def api_offenses(request):
    """Returns sorted specific crime heads for a single district and year (powers horizontal bar chart)."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    category = request.GET.get('category')
    try:
        limit = int(request.GET.get('limit', 12))
    except (ValueError, TypeError):
        limit = 12
    data = engine.get_district_offenses(district=district, year=year, category=category, limit=limit)
    response = JsonResponse({
        'offenses': data,
        'districts': data,  # backward compatibility alias
        'comparison': data, # backward compatibility alias
        'trends': data      # backward compatibility alias
    })
    return add_no_cache_headers(response)


def api_critical_offenses(request):
    """Returns violent/safety-critical crime heads for a single district and year."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    data = engine.get_district_critical_offenses(district=district, year=year)
    return add_no_cache_headers(JsonResponse({'critical_offenses': data}))


def api_categories(request):
    """Returns crime category distribution for a single district and year (powers donut chart)."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    data = engine.get_district_category_distribution(district=district, year=year)
    return add_no_cache_headers(JsonResponse(data))


def api_trends(request):
    """Returns multi-year annual trend trajectory (2016-2022) for the selected district."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    data = engine.get_district_multi_year_trend(district=district)
    return add_no_cache_headers(JsonResponse(data))


def api_district_detail(request):
    """Returns detailed profile for a single district and year."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    data = engine.get_district_summary(district=district, year=year)
    return add_no_cache_headers(JsonResponse(data))


def api_table_data(request):
    """Returns all 34 individual crime heads for a single district and year in table format."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')
    category = request.GET.get('category')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'count')
    sort_order = request.GET.get('order', 'desc')

    data = engine.get_district_table(
        district=district, year=year, category=category, search=search,
        sort_by=sort_by, sort_order=sort_order
    )
    return add_no_cache_headers(JsonResponse(data))


def api_export_csv(request):
    """Exports all 34 individual crime heads for the selected single district and year as a CSV file."""
    engine = CrimeDataEngine.get_instance()
    raw = request.GET.get('district') or request.GET.get('state')
    district = resolve_district(raw, engine.get_districts())
    year = request.GET.get('year', 'all')

    table_data = engine.get_district_table(district=district, year=year)
    year_str = "2016-2022" if year in ['all', 'combined'] else year

    filename = f"KCAVP_{district.replace(' ', '_')}_{year_str}_crime_profile.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'District', 'Parent District', 'State', 'Year',
        'Crime Head / Offense', 'Category', 'Incident Count', 'Share of District Total (%)', 'Severity Tier'
    ])

    for row in table_data['rows']:
        writer.writerow([
            table_data['district'], table_data['parent_district'], 'Karnataka', year_str,
            row['name'], row['category_label'], row['count'], row['percentage'], row['tier']
        ])

    return add_no_cache_headers(response)


@csrf_exempt
def api_chatbot(request):
    """Natural-language crime analytics query endpoint analyzing all 38 districts."""
    engine = CrimeChatbotEngine.get_instance()

    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            query = body.get('query', '')
            district = body.get('district', '')
            year = body.get('year', 'all')
            pinned_district = body.get('pinned_district', None)
        except Exception:
            query = request.POST.get('query', '')
            district = request.POST.get('district', '')
            year = request.POST.get('year', 'all')
            pinned_district = request.POST.get('pinned_district', None)
    else:
        query = request.GET.get('query') or request.GET.get('q', '')
        district = request.GET.get('district', '')
        year = request.GET.get('year', 'all')
        pinned_district = request.GET.get('pinned_district', None)

    districts_list = engine.all_districts
    selected_district = resolve_district(district, districts_list) if district else 'Bengaluru City'

    result = engine.ask(
        query=query,
        selected_district=selected_district,
        selected_year=year or 'all',
        pinned_district=pinned_district
    )
    return add_no_cache_headers(JsonResponse(result))


def favicon(request):
    """Serves the platform SVG emblem for /favicon.ico to eliminate 404 terminal logs."""
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">⚖</text></svg>'
    response = HttpResponse(svg, content_type="image/svg+xml")
    return add_no_cache_headers(response)