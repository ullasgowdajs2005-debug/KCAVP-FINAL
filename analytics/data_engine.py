import csv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Metadata for all 34 individual IPC crime heads in the official dataset
CRIME_HEAD_META = {
    'murder': {'name': 'Murder', 'category': 'violent', 'icon': '⚔️'},
    'attempt_to_commit_murder': {'name': 'Attempt to Commit Murder', 'category': 'violent', 'icon': '⚡'},
    'culpable_homicide_not_amounting_to_murder': {'name': 'Culpable Homicide', 'category': 'violent', 'icon': '⚠️'},
    'attempt_to_commit_culpable_homicide': {'name': 'Attempted Culpable Homicide', 'category': 'violent', 'icon': '⚠️'},
    'rape': {'name': 'Rape', 'category': 'women_children', 'icon': '🛡️'},
    'attempt_to_commit_rape': {'name': 'Attempted Rape', 'category': 'women_children', 'icon': '🛡️'},
    'kidnapping_and_abduction': {'name': 'Kidnapping & Abduction', 'category': 'women_children', 'icon': '🚨'},
    'dacoity': {'name': 'Dacoity (Gang Robbery)', 'category': 'violent', 'icon': '🗡️'},
    'mkng_preparation_and_assembly_for_comm_dacoity': {'name': 'Preparation for Dacoity', 'category': 'other', 'icon': '🔍'},
    'robbery': {'name': 'Robbery', 'category': 'violent', 'icon': '💰'},
    'criminal_trespass_or_burglary': {'name': 'Burglary & Criminal Trespass', 'category': 'property_economic', 'icon': '🚪'},
    'theft': {'name': 'Theft', 'category': 'property_economic', 'icon': '💼'},
    'unlawful_assembly': {'name': 'Unlawful Assembly', 'category': 'public_order', 'icon': '👥'},
    'riots': {'name': 'Rioting', 'category': 'public_order', 'icon': '🔥'},
    'criminal_breach_of_trust': {'name': 'Criminal Breach of Trust', 'category': 'property_economic', 'icon': '🤝'},
    'cheating': {'name': 'Cheating & Fraud', 'category': 'property_economic', 'icon': '💳'},
    'forgery': {'name': 'Forgery', 'category': 'property_economic', 'icon': '📝'},
    'counterfeiting': {'name': 'Counterfeiting Currency/Goods', 'category': 'property_economic', 'icon': '💵'},
    'arson': {'name': 'Arson', 'category': 'violent', 'icon': '🔥'},
    'grievous_hurt': {'name': 'Grievous Hurt', 'category': 'violent', 'icon': '🩹'},
    'dowry_deaths': {'name': 'Dowry Deaths', 'category': 'women_children', 'icon': '⚠️'},
    'assault_on_women': {'name': 'Assault on Women (Modesty Outrage)', 'category': 'women_children', 'icon': '🛡️'},
    'insult_to_the_modesty_of_women': {'name': 'Insult to Modesty of Women', 'category': 'women_children', 'icon': '🛡️'},
    'cruelty_by_husband_or_his_relatives': {'name': 'Cruelty by Husband/Relatives (498A)', 'category': 'women_children', 'icon': '💔'},
    'importation_of_girls_from_foreign_country': {'name': 'Importation of Girls', 'category': 'women_children', 'icon': '🚨'},
    'causing_death_by_negligence': {'name': 'Causing Death by Negligence', 'category': 'public_safety', 'icon': '⚠️'},
    'offences_against_state': {'name': 'Offences Against the State', 'category': 'public_order', 'icon': '⚖️'},
    'offences_promoting_enmity_between_diff_grp': {'name': 'Promoting Enmity Between Groups', 'category': 'public_order', 'icon': '🗣️'},
    'extortion': {'name': 'Extortion & Blackmail', 'category': 'property_economic', 'icon': '💰'},
    'disclosure_of_identity_of_victims': {'name': 'Disclosure of Identity of Victims', 'category': 'other', 'icon': '🔒'},
    'incidence_of_rash_driving': {'name': 'Incidence of Rash Driving', 'category': 'public_safety', 'icon': '🚗'},
    'human_trafficking': {'name': 'Human Trafficking', 'category': 'women_children', 'icon': '🚨'},
    'unnatural_offence': {'name': 'Unnatural Offences', 'category': 'other', 'icon': '⚖️'},
    'other_ipc_crimes': {'name': 'Other IPC Crimes', 'category': 'other', 'icon': '📄'}
}

CATEGORY_NAMES = {
    'property_economic': 'Property & Economic Offences',
    'public_safety': 'Public Safety & Traffic Offences',
    'women_children': 'Crimes Against Women & Children',
    'violent': 'Violent Crimes',
    'public_order': 'Public Order & Rioting',
    'other': 'Other IPC Crimes'
}

CATEGORY_COLORS = {
    'property_economic': '#3b82f6',  # Blue
    'public_safety': '#f59e0b',      # Amber
    'women_children': '#ec4899',     # Pink
    'violent': '#f43f5e',           # Rose / Red
    'public_order': '#8b5cf6',       # Purple
    'other': '#64748b'               # Slate
}


class CrimeDataEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.records = []
        self.districts = []
        self.years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']
        self.records_by_district_year = {}
        self.aggregated_by_district = {}
        self.state_name = "Karnataka"
        self._load_datasets()

    def _load_datasets(self):
        file_path = BASE_DIR / 'karnataka_crime_data.csv'
        if not os.path.exists(file_path):
            file_path = BASE_DIR / 'districtwise-ipc-crimes-2016.csv'

        records = []
        districts_set = set()
        by_district_year = {}
        years_found = set()

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = (row.get('state_name') or '').strip()
                    if state != 'Karnataka':
                        continue

                    year = (row.get('year') or '2016').strip()
                    years_found.add(year)

                    circle = (row.get('registration_circles') or '').strip()
                    parent_district = (row.get('district_name') or '').strip()
                    district_display = circle if circle else parent_district

                    cat_totals = {
                        'violent': 0,
                        'women_children': 0,
                        'property_economic': 0,
                        'public_safety': 0,
                        'public_order': 0,
                        'other': 0
                    }
                    total_crimes = 0
                    raw_crimes = {}

                    for col, val in row.items():
                        if col in ['id', 'year', 'state_name', 'state_code', 'district_name', 'district_code', 'registration_circles']:
                            continue
                        try:
                            num = int(val or 0)
                        except (ValueError, TypeError):
                            num = 0
                        raw_crimes[col] = num
                        total_crimes += num

                        meta = CRIME_HEAD_META.get(col)
                        if meta:
                            cat_totals[meta['category']] += num

                    rec = {
                        'id': row.get('id', ''),
                        'year': year,
                        'state': 'Karnataka',
                        'district': district_display,
                        'parent_district': parent_district,
                        'circle': circle,
                        'total_crimes': total_crimes,
                        'categories': cat_totals,
                        'crimes': raw_crimes
                    }
                    records.append(rec)
                    districts_set.add(district_display)
                    by_district_year[(district_display.lower(), year)] = rec

        self.records = records
        self.districts = sorted(list(districts_set))
        if years_found:
            self.years = sorted(list(years_found))
        self.records_by_district_year = by_district_year

        # Pre-calculate multi-year aggregate for every district across 2016-2022
        min_year = self.years[0] if self.years else '2016'
        max_year = self.years[-1] if self.years else '2022'
        period_str = f"{min_year}–{max_year}"

        agg_map = {}
        for d in self.districts:
            d_records = [r for r in records if r['district'] == d]
            if not d_records:
                continue

            agg_total = sum(r['total_crimes'] for r in d_records)
            agg_cats = {c: 0 for c in CATEGORY_NAMES}
            agg_crimes = {c: 0 for c in CRIME_HEAD_META}

            for r in d_records:
                for cat, val in r['categories'].items():
                    agg_cats[cat] = agg_cats.get(cat, 0) + val
                for crime, val in r['crimes'].items():
                    agg_crimes[crime] = agg_crimes.get(crime, 0) + val

            agg_map[d.lower()] = {
                'id': f'agg_{d}',
                'year': f'{min_year}-{max_year}',
                'year_display': f'All Years ({period_str})',
                'state': 'Karnataka',
                'district': d,
                'parent_district': d_records[0]['parent_district'],
                'circle': d_records[0]['circle'],
                'total_crimes': agg_total,
                'categories': agg_cats,
                'crimes': agg_crimes,
                'annual_records': {r['year']: r for r in d_records}
            }
        self.aggregated_by_district = agg_map

    def get_districts(self, state=None):
        return self.districts

    def get_years(self):
        # Return all years descending, with 'all' first
        desc_years = sorted(self.years, reverse=True)
        return ['all'] + desc_years

    def _resolve_district_name(self, district):
        if not district or district.lower() in ['all', 'default', 'none', 'null']:
            return 'Bengaluru City' if 'Bengaluru City' in self.districts else self.districts[0]

        d_lower = district.lower().strip()
        for d in self.districts:
            if d.lower() == d_lower:
                return d
        for d in self.districts:
            if d_lower in d.lower():
                return d
        for r in self.records:
            if d_lower in r['parent_district'].lower():
                return r['district']
        return 'Bengaluru City' if 'Bengaluru City' in self.districts else self.districts[0]

    def get_record(self, district=None, year=None):
        """Fetches a district record for a specific year (2016-2022) or aggregate ('all')."""
        d_name = self._resolve_district_name(district)
        d_key = d_name.lower()

        clean_year = str(year).strip().lower() if year else 'all'
        if clean_year in ['all', 'combined', 'total', '2016-2022', 'none']:
            if d_key in self.aggregated_by_district:
                return self.aggregated_by_district[d_key]
            rec = next((r for r in self.records if r['district'].lower() == d_key), None)
            return rec or self.records[0]

        # Specific year lookup
        match = self.records_by_district_year.get((d_key, clean_year))
        if match:
            return match

        # If district was newly carved out in later years, synthesize a zero-crime profile for earlier years
        parent_rec = self.records_by_district_year.get((d_key, self.years[-1]))
        parent_district = parent_rec['parent_district'] if parent_rec else d_name
        return {
            'id': f'{clean_year}_{d_name}',
            'year': clean_year,
            'state': 'Karnataka',
            'district': d_name,
            'parent_district': parent_district,
            'circle': d_name,
            'total_crimes': 0,
            'categories': {c: 0 for c in CATEGORY_NAMES},
            'crimes': {c: 0 for c in CRIME_HEAD_META}
        }

    def get_district_summary(self, district='Bengaluru City', year='all'):
        """Computes executive KPIs for the selected district and year with YoY growth calculations."""
        clean_year = str(year).strip().lower() if year else 'all'
        r = self.get_record(district, year=clean_year)
        d_name = r['district']
        total = r['total_crimes']
        cats = r['categories']
        crimes = r['crimes']

        specific_crimes = {k: v for k, v in crimes.items() if k != 'other_ipc_crimes'}
        top_key, top_val = max(specific_crimes.items(), key=lambda x: x[1]) if specific_crimes else ('theft', 0)
        top_name = CRIME_HEAD_META.get(top_key, {}).get('name', top_key.replace('_', ' ').title())

        cat_pcts = {}
        for cat, val in cats.items():
            cat_pcts[cat] = round((val / total) * 100, 1) if total > 0 else 0

        homicides = crimes.get('murder', 0) + crimes.get('attempt_to_commit_murder', 0)
        thefts_burglaries = crimes.get('theft', 0) + crimes.get('criminal_trespass_or_burglary', 0)
        women_assaults = crimes.get('assault_on_women', 0) + crimes.get('rape', 0)
        traffic_accidents = crimes.get('incidence_of_rash_driving', 0) + crimes.get('causing_death_by_negligence', 0)

        # Build complete annual trajectory for all available years
        annual_trajectory = {}
        for y in self.years:
            yr_rec = self.records_by_district_year.get((d_name.lower(), y))
            annual_trajectory[y] = yr_rec['total_crimes'] if yr_rec else 0

        # Dynamic YoY Growth calculations
        prev_year = None
        yoy_growth = 0.0

        if clean_year in self.years:
            idx = self.years.index(clean_year)
            if idx > 0:
                prev_yr_str = self.years[idx - 1]
                prev_year = prev_yr_str
                prev_tot = annual_trajectory.get(prev_yr_str, 0)
                if prev_tot > 0:
                    yoy_growth = round(((total - prev_tot) / prev_tot) * 100, 1)
        else:
            first_y = self.years[0]
            last_y = self.years[-1]
            prev_year = f"{first_y} vs {last_y}"
            first_tot = annual_trajectory.get(first_y, 0)
            last_tot = annual_trajectory.get(last_y, 0)
            if first_tot > 0:
                yoy_growth = round(((last_tot - first_tot) / first_tot) * 100, 1)

        year_display = f'All Years ({self.years[0]}–{self.years[-1]})' if clean_year in ['all', 'combined'] else f'Year {clean_year}'

        return {
            'district': d_name,
            'parent_district': r['parent_district'],
            'state': 'Karnataka',
            'year': clean_year,
            'year_display': year_display,
            'total_crimes': total,
            'total': total,  # alias for backward compatibility
            'violent': cats.get('violent', 0),
            'women_children': cats.get('women_children', 0),
            'property_economic': cats.get('property_economic', 0),
            'public_safety': cats.get('public_safety', 0),
            'public_order': cats.get('public_order', 0),
            'other': cats.get('other', 0),
            'categories': cats,
            'category_percentages': cat_pcts,
            'top_offense': {
                'key': top_key,
                'name': top_name,
                'count': top_val,
                'percentage': round((top_val / total) * 100, 1) if total > 0 else 0
            },
            'top_district': d_name,
            'top_district_count': total,
            'prev_year': prev_year,
            'yoy_growth': yoy_growth,
            'annual_trajectory': annual_trajectory,
            'key_highlights': {
                'homicides': homicides,
                'thefts_burglaries': thefts_burglaries,
                'women_assaults': women_assaults,
                'traffic_accidents': traffic_accidents,
                'cheating': crimes.get('cheating', 0),
                'riots': crimes.get('riots', 0),
            }
        }

    def get_district_offenses(self, district='Bengaluru City', year='all', category=None, limit=12):
        """Returns sorted list of specific individual crime heads for this district and year."""
        r = self.get_record(district, year=year)
        total = r['total_crimes']
        crimes = r['crimes']

        offenses = []
        for key, count in crimes.items():
            meta = CRIME_HEAD_META.get(key, {'name': key.replace('_', ' ').title(), 'category': 'other', 'icon': '📌'})
            cat = meta['category']

            if category and category.lower() != 'all' and cat.lower() != category.lower():
                continue

            pct = round((count / total) * 100, 1) if total > 0 else 0
            offenses.append({
                'key': key,
                'name': meta['name'],
                'category': cat,
                'category_label': CATEGORY_NAMES.get(cat, cat.title()),
                'color': CATEGORY_COLORS.get(cat, '#64748b'),
                'icon': meta['icon'],
                'count': count,
                'percentage': pct,
                # Aliases for backward compatibility
                'district': meta['name'],
                'total': count
            })

        offenses.sort(key=lambda x: x['count'], reverse=True)
        if limit and limit > 0:
            return offenses[:limit]
        return offenses

    def get_district_category_distribution(self, district='Bengaluru City', year='all'):
        """Returns the 6 category breakdown for the donut chart of this single district and year."""
        r = self.get_record(district, year=year)
        total = r['total_crimes']
        cats = r['categories']

        result = []
        for cat, label in CATEGORY_NAMES.items():
            cnt = cats.get(cat, 0)
            pct = round((cnt / total) * 100, 1) if total > 0 else 0
            result.append({
                'id': cat,
                'label': label,
                'count': cnt,
                'percentage': pct,
                'color': CATEGORY_COLORS.get(cat, '#64748b')
            })

        return {
            'district': r['district'],
            'year': r.get('year', year),
            'total': total,
            'categories': result
        }

    def get_district_critical_offenses(self, district='Bengaluru City', year='all'):
        """Safety-critical offenses for this single district and year."""
        r = self.get_record(district, year=year)
        crimes = r['crimes']

        critical_keys = [
            'murder', 'attempt_to_commit_murder', 'rape',
            'kidnapping_and_abduction', 'robbery', 'dacoity',
            'grievous_hurt', 'arson', 'riots'
        ]

        data = []
        for k in critical_keys:
            meta = CRIME_HEAD_META.get(k, {'name': k, 'category': 'violent', 'icon': '⚡'})
            cnt = crimes.get(k, 0)
            data.append({
                'key': k,
                'name': meta['name'],
                'category': meta['category'],
                'icon': meta['icon'],
                'count': cnt
            })

        data.sort(key=lambda x: x['count'], reverse=True)
        return data

    def get_district_multi_year_trend(self, district='Bengaluru City'):
        """Returns full annual timeline from 2016 to 2022 for the selected district."""
        d_name = self._resolve_district_name(district)
        parent_district = d_name

        series_list = []
        for y in self.years:
            r = self.records_by_district_year.get((d_name.lower(), y))
            if r:
                parent_district = r['parent_district']
                series_list.append({
                    'year': y,
                    'total': r['total_crimes'],
                    'violent': r['categories']['violent'],
                    'property_economic': r['categories']['property_economic'],
                    'public_safety': r['categories']['public_safety'],
                    'women_children': r['categories']['women_children'],
                    'public_order': r['categories']['public_order'],
                    'other': r['categories']['other'],
                    'theft': r['crimes'].get('theft', 0),
                    'murder': r['crimes'].get('murder', 0)
                })
            else:
                series_list.append({
                    'year': y,
                    'total': 0,
                    'violent': 0,
                    'property_economic': 0,
                    'public_safety': 0,
                    'women_children': 0,
                    'public_order': 0,
                    'other': 0,
                    'theft': 0,
                    'murder': 0
                })

        return {
            'district': d_name,
            'parent_district': parent_district,
            'years': list(self.years),
            'totals': [s['total'] for s in series_list],
            'series': series_list
        }

    def get_district_table(self, district='Bengaluru City', year='all', category=None, search='', sort_by='count', sort_order='desc'):
        """Returns all 34 individual IPC crime heads for this district and year."""
        clean_year = str(year).strip().lower() if year else 'all'
        r = self.get_record(district, year=clean_year)
        total = r['total_crimes']
        crimes = r['crimes']

        rows = []
        for key, count in crimes.items():
            meta = CRIME_HEAD_META.get(key, {'name': key.replace('_', ' ').title(), 'category': 'other', 'icon': '📌'})
            cat = meta['category']

            if category and category.lower() != 'all' and cat.lower() != category.lower():
                continue

            name = meta['name']
            if search:
                s = search.lower().strip()
                if s not in name.lower() and s not in cat.lower():
                    continue

            pct = round((count / total) * 100, 2) if total > 0 else 0.0

            threshold_high = 500 if clean_year != 'all' else 2500
            threshold_mod = 100 if clean_year != 'all' else 500

            if count > threshold_high or cat == 'violent':
                tier = 'High Focus'
                tier_badge = 'danger'
            elif count > threshold_mod or cat == 'women_children':
                tier = 'Moderate'
                tier_badge = 'warning'
            else:
                tier = 'Low Frequency'
                tier_badge = 'info'

            rows.append({
                'key': key,
                'name': name,
                'district': name,            # backward compatibility for old scripts
                'state': r['district'],      # backward compatibility for old scripts
                'total': count,              # backward compatibility for old scripts
                'violent': count if cat == 'violent' else 0,
                'women_children': count if cat == 'women_children' else 0,
                'property_economic': count if cat == 'property_economic' else 0,
                'public_safety': count if cat == 'public_safety' else 0,
                'murder': count if key == 'murder' else 0,
                'theft': count if key == 'theft' else 0,
                'category': cat,
                'category_label': CATEGORY_NAMES.get(cat, cat.title()),
                'color': CATEGORY_COLORS.get(cat, '#64748b'),
                'icon': meta['icon'],
                'count': count,
                'percentage': pct,
                'tier': tier,
                'tier_badge': tier_badge
            })

        reverse = (sort_order.lower() != 'asc')
        if sort_by == 'name':
            rows.sort(key=lambda x: x['name'].lower(), reverse=reverse)
        elif sort_by == 'category':
            rows.sort(key=lambda x: x['category_label'].lower(), reverse=reverse)
        else:
            rows.sort(key=lambda x: x['count'], reverse=reverse)

        return {
            'district': r['district'],
            'parent_district': r['parent_district'],
            'year': clean_year,
            'total_crimes': total,
            'total_heads': len(rows),
            'page': 1,
            'page_size': len(rows),
            'total_pages': 1,
            'total_rows': len(rows),
            'rows': rows
        }

    # Backward compatibility helpers
    def get_summary(self, district='Bengaluru City', **kwargs):
        year = kwargs.get('year', 'all')
        return self.get_district_summary(district, year=year)

    def get_category_breakdown(self, district='Bengaluru City', **kwargs):
        year = kwargs.get('year', 'all')
        return self.get_district_category_distribution(district, year=year)

    def get_district_detail(self, district='Bengaluru City', **kwargs):
        year = kwargs.get('year', 'all')
        return self.get_district_summary(district, year=year)

    def get_table_data(self, district='Bengaluru City', **kwargs):
        dist = kwargs.get('district') or kwargs.get('state') or district
        year = kwargs.get('year', 'all')
        return self.get_district_table(district=dist, year=year, **kwargs)
