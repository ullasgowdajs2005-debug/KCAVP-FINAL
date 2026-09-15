import csv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Standardized Crime Categories mapping across 2016 and 2017+ schemas
CATEGORY_MAPPINGS_2016 = {
    'violent': [
        'murder', 'attempt_to_commit_murder',
        'culpable_homicide_not_amounting_to_murder',
        'attempt_to_commit_culpable_homicide',
        'dacoity', 'robbery', 'grievous_hurt', 'arson'
    ],
    'women_children': [
        'rape', 'attempt_to_commit_rape', 'assault_on_women',
        'insult_to_the_modesty_of_women', 'cruelty_by_husband_or_his_relatives',
        'dowry_deaths', 'kidnapping_and_abduction',
        'human_trafficking', 'importation_of_girls_from_foreign_country'
    ],
    'property_economic': [
        'theft', 'criminal_trespass_or_burglary', 'cheating',
        'forgery', 'counterfeiting', 'criminal_breach_of_trust', 'extortion'
    ],
    'public_safety': [
        'incidence_of_rash_driving', 'causing_death_by_negligence'
    ],
    'public_order': [
        'riots', 'unlawful_assembly', 'offences_against_state',
        'offences_promoting_enmity_between_diff_grp'
    ],
    'other': [
        'other_ipc_crimes', 'unnatural_offence', 'disclosure_of_identity_of_victims',
        'mkng_preparation_and_assembly_for_comm_dacoity'
    ]
}

CATEGORY_MAPPINGS_2017 = {
    'violent': [
        'murder', 'clpbl_hmcrd_not_amt_murder', 'atmpt_cmmt_murder',
        'atmpt_cmmt_clpb_hmcrd', 'atmpt_cmmt_suicide', 'abetment_of_suicide',
        'vlntrly_caus_simple_hurt', 'vlntrly_caus_dangers_weapons',
        'vlntrly_caus_pub_srvnt_duty', 'hrt_endgrng_lf_safety', 'other_simple_hurt',
        'vlntrly_caus_grvus_hurt', 'grvus_hrt_dangerous_wepn', 'grvus_hrt_pub_srvnt_duty',
        'grvus_hrt_lf_safety', 'other_grievous_hurt', 'acid_attack', 'atmpt_acid_attack',
        'dacoity', 'dacoity_with_murder', 'robbery', 'atmpt_dacoity_robbery',
        'mkng_prprtn_assmbly_cmmttng_dcty', 'arson'
    ],
    'women_children': [
        'rape', 'atmpt_rape', 'dowry_deaths', 'assault_on_women',
        'crlty_husbnd_relatives', 'insult_modesty_women', 'stalking',
        'voyeurism', 'intnt_disrbe', 'sex_hrrsmt_work_office_prms',
        'sex_hrrsmt_pub_trnsprt_sys', 'sex_hrrsmt_shelter_homes',
        'sex_hrrsmt_other_places', 'missing_child_kidnpd', 'other_kidnp_abduc',
        'kidnp_abdctn_begging', 'kidnp_abdctn_murder', 'kidnapping_for_ransom',
        'kidnp_abdctn_marrg', 'proc_minor_girls', 'import_girls_frgn_cntry',
        'other_kidnp_abduc_sec_365_369', 'human_trafficking', 'exp_traf_person',
        'sell_minors_prost', 'buy_minors_prost', 'miscarr_infant_foetic_aband'
    ],
    'property_economic': [
        'auto_motor_vehicle_theft', 'other_thefts', 'day_time_burglary',
        'night_burglary', 'criminal_trespass', 'cheating', 'cheating_impersonation',
        'forgery', 'criminal_breach_of_trust', 'criminal_misappropriation',
        'dsh_hon_rec_deal_stl_prop', 'extortion_and_blackmailing',
        'counterfeit_coin', 'cntrfte_govt_stamp', 'cntrft_seal_mark',
        'cntrft_curr_bank_notes', 'bank_frauds', 'atm_fraud',
        'credit_debit_card_fraud', 'other_frauds'
    ],
    'public_safety': [
        'rash_driving_pub_way', 'csng_hrt_rsh_nglgnt_drvng_pblc_wy',
        'grvus_hrt_rsh_nglgnt_drvng', 'hit_and_run', 'acdnt_other_than_hit_and_run_',
        'deaths_negl_rel_rail_acdnt', 'deaths_due_med_negnc',
        'deaths_neg_civic_bodies', 'deaths_other_negnc', 'obstruction_pub_way'
    ],
    'public_order': [
        'rioting_communal_religious', 'rioting_sectarian', 'rioting_industrial',
        'rioting_political', 'rioting_caste_conflict', 'rioting_agrarian',
        'rioting_students', 'rioting_vigilants', 'rioting_money_dispute',
        'rioting_water_dispute', 'rioting_land_property_dispute',
        'rioting_family_disputes', 'rioting_enmity_rivalry', 'riot_elec_pwr_disp',
        'riot_andolan_morcha', 'riot_polc_prsnl_gvt_srvnt', 'other_rioting',
        'prmt_enmty_grps', 'impt_asrtns_prjudc_intgrtn', 'affray',
        'ofnc_agnst_state_sedition', 'ofnc_agnst_state_other',
        'ofnc_agnst_pub_trnqul', 'disbnc_ordr_prmlgtd_pblc_srvnt'
    ],
    'other': [
        'other_ipc_crimes', 'unnatural_offences', 'wrngful_rest_cnfm',
        'ofnc_elections', 'harboring_offender', 'sale_food_drugs',
        'sale_obscene_books_objects', 'obscene_acts_songs_public_places',
        'ofnc_religion', 'ofnc_mischief', 'crcl_false_fake_news_rumours',
        'criminal_intimidation'
    ]
}

CATEGORY_NAMES = {
    'violent': 'Violent Crimes',
    'women_children': 'Crimes Against Women & Children',
    'property_economic': 'Property & Economic Offences',
    'public_safety': 'Public Safety & Traffic Offences',
    'public_order': 'Public Order & Rioting',
    'other': 'Other IPC Crimes'
}

CATEGORY_COLORS = {
    'violent': '#f43f5e',           # Rose / Red
    'women_children': '#ec4899',     # Pink
    'property_economic': '#3b82f6',  # Blue
    'public_safety': '#f59e0b',      # Amber
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
        self.states = []
        self.districts_by_state = {}
        self.years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']
        self._load_datasets()

    def _clean_district_name(self, name):
        if not name:
            return "Unknown"
        name = name.strip()
        # Normalize minor title differences
        return name

    def _load_datasets(self):
        path_2016 = BASE_DIR / 'districtwise-ipc-crimes-2016.csv'
        path_onwards = BASE_DIR / 'districtwise-ipc-crimes-2017-onwards.csv'

        records = []
        states_set = set()
        districts_map = {}

        # 1. Ingest 2016 CSV
        if os.path.exists(path_2016):
            with open(path_2016, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = (row.get('state_name') or '').strip()
                    if not state:
                        continue
                    district = self._clean_district_name(row.get('district_name'))
                    states_set.add(state)
                    districts_map.setdefault(state, set()).add(district)

                    # Compute category totals and total crimes
                    cat_totals = {'violent': 0, 'women_children': 0, 'property_economic': 0, 'public_safety': 0, 'public_order': 0, 'other': 0}
                    total_crimes = 0
                    raw_numeric = {}

                    for col, val in row.items():
                        if col in ['id', 'year', 'state_name', 'state_code', 'district_name', 'district_code', 'registration_circles']:
                            continue
                        try:
                            num = int(val or 0)
                        except (ValueError, TypeError):
                            num = 0
                        raw_numeric[col] = num
                        total_crimes += num

                        for cat, cols in CATEGORY_MAPPINGS_2016.items():
                            if col in cols:
                                cat_totals[cat] += num
                                break

                    rec = {
                        'id': row.get('id', ''),
                        'year': '2016',
                        'state': state,
                        'district': district,
                        'circle': (row.get('registration_circles') or '').strip(),
                        'total_crimes': total_crimes,
                        'categories': cat_totals,
                        'key_metrics': {
                            'murder': raw_numeric.get('murder', 0),
                            'attempt_murder': raw_numeric.get('attempt_to_commit_murder', 0),
                            'rape': raw_numeric.get('rape', 0),
                            'assault_on_women': raw_numeric.get('assault_on_women', 0),
                            'kidnapping': raw_numeric.get('kidnapping_and_abduction', 0),
                            'theft': raw_numeric.get('theft', 0),
                            'robbery': raw_numeric.get('robbery', 0),
                            'dacoity': raw_numeric.get('dacoity', 0),
                            'cheating': raw_numeric.get('cheating', 0),
                            'burglary': raw_numeric.get('criminal_trespass_or_burglary', 0),
                            'rash_driving': raw_numeric.get('incidence_of_rash_driving', 0),
                            'riots': raw_numeric.get('riots', 0),
                        },
                        'raw': raw_numeric
                    }
                    records.append(rec)

        # 2. Ingest 2017-2022 CSV
        if os.path.exists(path_onwards):
            with open(path_onwards, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    state = (row.get('state_name') or '').strip()
                    if not state:
                        continue
                    district = self._clean_district_name(row.get('district_name'))
                    year = (row.get('year') or '').strip()
                    states_set.add(state)
                    districts_map.setdefault(state, set()).add(district)

                    cat_totals = {'violent': 0, 'women_children': 0, 'property_economic': 0, 'public_safety': 0, 'public_order': 0, 'other': 0}
                    total_crimes = 0
                    raw_numeric = {}

                    for col, val in row.items():
                        if col in ['id', 'year', 'state_name', 'state_code', 'district_name', 'district_code', 'registration_circles']:
                            continue
                        try:
                            num = int(val or 0)
                        except (ValueError, TypeError):
                            num = 0
                        raw_numeric[col] = num
                        total_crimes += num

                        for cat, cols in CATEGORY_MAPPINGS_2017.items():
                            if col in cols:
                                cat_totals[cat] += num
                                break

                    # Key metrics normalization
                    theft_sum = raw_numeric.get('auto_motor_vehicle_theft', 0) + raw_numeric.get('other_thefts', 0)
                    burglary_sum = raw_numeric.get('day_time_burglary', 0) + raw_numeric.get('night_burglary', 0) + raw_numeric.get('criminal_trespass', 0)
                    kidnap_sum = (raw_numeric.get('missing_child_kidnpd', 0) + raw_numeric.get('other_kidnp_abduc', 0) +
                                  raw_numeric.get('kidnp_abdctn_begging', 0) + raw_numeric.get('kidnp_abdctn_murder', 0) +
                                  raw_numeric.get('kidnapping_for_ransom', 0) + raw_numeric.get('kidnp_abdctn_marrg', 0) +
                                  raw_numeric.get('other_kidnp_abduc_sec_365_369', 0))
                    rash_sum = raw_numeric.get('rash_driving_pub_way', 0) + raw_numeric.get('csng_hrt_rsh_nglgnt_drvng_pblc_wy', 0)
                    riots_sum = sum(v for k, v in raw_numeric.items() if k.startswith('rioting_') or k.startswith('riot_'))

                    rec = {
                        'id': row.get('id', ''),
                        'year': year,
                        'state': state,
                        'district': district,
                        'circle': (row.get('registration_circles') or '').strip(),
                        'total_crimes': total_crimes,
                        'categories': cat_totals,
                        'key_metrics': {
                            'murder': raw_numeric.get('murder', 0),
                            'attempt_murder': raw_numeric.get('atmpt_cmmt_murder', 0),
                            'rape': raw_numeric.get('rape', 0),
                            'assault_on_women': raw_numeric.get('assault_on_women', 0),
                            'kidnapping': kidnap_sum,
                            'theft': theft_sum,
                            'robbery': raw_numeric.get('robbery', 0),
                            'dacoity': raw_numeric.get('dacoity', 0) + raw_numeric.get('dacoity_with_murder', 0),
                            'cheating': raw_numeric.get('cheating', 0) + raw_numeric.get('bank_frauds', 0) + raw_numeric.get('atm_fraud', 0),
                            'burglary': burglary_sum,
                            'rash_driving': rash_sum,
                            'riots': riots_sum,
                        },
                        'raw': raw_numeric
                    }
                    records.append(rec)

        self.records = records
        # Put Karnataka first in states list if present, then alphabetical
        all_states = sorted(list(states_set))
        if 'Karnataka' in all_states:
            all_states.remove('Karnataka')
            all_states.insert(0, 'Karnataka')
        self.states = all_states
        self.districts_by_state = {s: sorted(list(districts_map[s])) for s in districts_map}

    def get_states(self):
        return self.states

    def get_districts(self, state=None):
        if not state or state.lower() in ['all', 'all india']:
            all_d = set()
            for dlist in self.districts_by_state.values():
                all_d.update(dlist)
            return sorted(list(all_d))
        return self.districts_by_state.get(state, [])

    def filter_records(self, state=None, year=None, district=None):
        res = self.records
        if state and state.lower() not in ['all', 'all india']:
            res = [r for r in res if r['state'].lower() == state.lower()]
        if year and year.lower() not in ['all', 'all years']:
            res = [r for r in res if r['year'] == str(year)]
        if district and district.lower() not in ['all', 'all districts']:
            res = [r for r in res if r['district'].lower() == district.lower()]
        return res

    def get_summary(self, state='Karnataka', year='2022'):
        """Computes executive KPIs, YoY deltas, and breakdown for selected state & year."""
        current_records = self.filter_records(state=state, year=year)

        # Total crimes and category sums
        total_crimes = sum(r['total_crimes'] for r in current_records)
        cat_sums = {
            'violent': sum(r['categories']['violent'] for r in current_records),
            'women_children': sum(r['categories']['women_children'] for r in current_records),
            'property_economic': sum(r['categories']['property_economic'] for r in current_records),
            'public_safety': sum(r['categories']['public_safety'] for r in current_records),
            'public_order': sum(r['categories']['public_order'] for r in current_records),
            'other': sum(r['categories']['other'] for r in current_records),
        }

        # Key metrics aggregated
        key_metrics_sum = {
            'murder': sum(r['key_metrics']['murder'] for r in current_records),
            'attempt_murder': sum(r['key_metrics']['attempt_murder'] for r in current_records),
            'rape': sum(r['key_metrics']['rape'] for r in current_records),
            'assault_on_women': sum(r['key_metrics']['assault_on_women'] for r in current_records),
            'kidnapping': sum(r['key_metrics']['kidnapping'] for r in current_records),
            'theft': sum(r['key_metrics']['theft'] for r in current_records),
            'robbery': sum(r['key_metrics']['robbery'] for r in current_records),
            'dacoity': sum(r['key_metrics']['dacoity'] for r in current_records),
            'cheating': sum(r['key_metrics']['cheating'] for r in current_records),
            'burglary': sum(r['key_metrics']['burglary'] for r in current_records),
            'rash_driving': sum(r['key_metrics']['rash_driving'] for r in current_records),
            'riots': sum(r['key_metrics']['riots'] for r in current_records),
        }

        # District ranking to find top district
        district_totals = {}
        for r in current_records:
            d = r['district']
            district_totals[d] = district_totals.get(d, 0) + r['total_crimes']

        top_district = None
        top_district_count = 0
        if district_totals:
            top_district, top_district_count = max(district_totals.items(), key=lambda x: x[1])

        # Previous year delta calculation
        prev_year = str(int(year) - 1) if year and year.isdigit() and int(year) > 2016 else None
        prev_total = 0
        yoy_growth = 0.0
        yoy_diff = 0
        if prev_year:
            prev_records = self.filter_records(state=state, year=prev_year)
            prev_total = sum(r['total_crimes'] for r in prev_records)
            if prev_total > 0:
                yoy_diff = total_crimes - prev_total
                yoy_growth = round(((total_crimes - prev_total) / prev_total) * 100, 2)

        district_count = len(district_totals)

        return {
            'state': state,
            'year': year,
            'total_crimes': total_crimes,
            'prev_year': prev_year,
            'prev_total': prev_total,
            'yoy_growth': yoy_growth,
            'yoy_diff': yoy_diff,
            'district_count': district_count,
            'top_district': top_district,
            'top_district_count': top_district_count,
            'categories': cat_sums,
            'key_metrics': key_metrics_sum
        }

    def get_trends(self, state='Karnataka', district=None):
        """Returns longitudinal 2016-2022 trajectory for state or district."""
        years_list = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']
        trend_data = []

        for yr in years_list:
            recs = self.filter_records(state=state, year=yr, district=district)
            tot = sum(r['total_crimes'] for r in recs)
            v = sum(r['categories']['violent'] for r in recs)
            w = sum(r['categories']['women_children'] for r in recs)
            p = sum(r['categories']['property_economic'] for r in recs)
            s = sum(r['categories']['public_safety'] for r in recs)
            o = sum(r['categories']['public_order'] for r in recs)
            trend_data.append({
                'year': yr,
                'total': tot,
                'violent': v,
                'women_children': w,
                'property_economic': p,
                'public_safety': s,
                'public_order': o
            })

        return trend_data

    def get_district_rankings(self, state='Karnataka', year='2022', metric='total', limit=15):
        """Returns top districts ranked by metric."""
        recs = self.filter_records(state=state, year=year)
        agg = {}

        for r in recs:
            d = r['district']
            if d not in agg:
                agg[d] = {
                    'district': d,
                    'state': r['state'],
                    'total': 0,
                    'violent': 0,
                    'women_children': 0,
                    'property_economic': 0,
                    'public_safety': 0,
                    'public_order': 0,
                    'murder': 0,
                    'theft': 0,
                    'rape': 0
                }
            agg[d]['total'] += r['total_crimes']
            agg[d]['violent'] += r['categories']['violent']
            agg[d]['women_children'] += r['categories']['women_children']
            agg[d]['property_economic'] += r['categories']['property_economic']
            agg[d]['public_safety'] += r['categories']['public_safety']
            agg[d]['public_order'] += r['categories']['public_order']
            agg[d]['murder'] += r['key_metrics']['murder']
            agg[d]['theft'] += r['key_metrics']['theft']
            agg[d]['rape'] += r['key_metrics']['rape']

        rank_key = metric if metric in ['violent', 'women_children', 'property_economic', 'public_safety', 'public_order', 'murder', 'theft', 'rape'] else 'total'
        sorted_districts = sorted(agg.values(), key=lambda x: x[rank_key], reverse=True)

        if limit and limit > 0:
            return sorted_districts[:limit]
        return sorted_districts

    def get_category_breakdown(self, state='Karnataka', year='2022', district=None):
        """Returns category breakdown with percentages and sub-crime highlights."""
        recs = self.filter_records(state=state, year=year, district=district)
        cat_sums = {k: 0 for k in CATEGORY_NAMES}

        for r in recs:
            for cat in cat_sums:
                cat_sums[cat] += r['categories'][cat]

        total = sum(cat_sums.values())
        result = []
        for cat, label in CATEGORY_NAMES.items():
            cnt = cat_sums[cat]
            pct = round((cnt / total) * 100, 1) if total > 0 else 0
            result.append({
                'id': cat,
                'label': label,
                'count': cnt,
                'percentage': pct,
                'color': CATEGORY_COLORS[cat]
            })

        return {
            'total': total,
            'categories': result
        }

    def get_district_detail(self, state='Karnataka', district='Bengaluru Urban'):
        """Comprehensive deep dive profile for a single district."""
        d_lower = district.lower().strip()
        s_lower = state.lower().strip() if state and state.lower() not in ['all', 'all india'] else None

        # 1. Exact match on district_name
        dist_records = [r for r in self.records if (not s_lower or r['state'].lower() == s_lower) and r['district'].lower() == d_lower]

        # 2. Match on circle if not found
        if not dist_records:
            dist_records = [r for r in self.records if (not s_lower or r['state'].lower() == s_lower) and r['circle'].lower() == d_lower]

        # 3. Partial substring match on district_name
        if not dist_records:
            dist_records = [r for r in self.records if (not s_lower or r['state'].lower() == s_lower) and (d_lower in r['district'].lower() or r['district'].lower() in d_lower)]

        # 4. Partial substring match on circle
        if not dist_records:
            dist_records = [r for r in self.records if (not s_lower or r['state'].lower() == s_lower) and (d_lower in r['circle'].lower() or r['circle'].lower() in d_lower)]

        if not dist_records:
            return {'error': f'District {district} not found'}

        matched_district = dist_records[0]['district']
        matched_state = dist_records[0]['state']

        # Year-by-year trajectory
        years_dict = {}
        for r in dist_records:
            yr = r['year']
            years_dict.setdefault(yr, {
                'year': yr,
                'total': 0,
                'violent': 0,
                'women_children': 0,
                'property_economic': 0,
                'public_safety': 0,
                'public_order': 0,
                'murder': 0,
                'rape': 0,
                'theft': 0,
                'rash_driving': 0
            })
            years_dict[yr]['total'] += r['total_crimes']
            years_dict[yr]['violent'] += r['categories']['violent']
            years_dict[yr]['women_children'] += r['categories']['women_children']
            years_dict[yr]['property_economic'] += r['categories']['property_economic']
            years_dict[yr]['public_safety'] += r['categories']['public_safety']
            years_dict[yr]['public_order'] += r['categories']['public_order']
            years_dict[yr]['murder'] += r['key_metrics']['murder']
            years_dict[yr]['rape'] += r['key_metrics']['rape']
            years_dict[yr]['theft'] += r['key_metrics']['theft']
            years_dict[yr]['rash_driving'] += r['key_metrics']['rash_driving']

        timeline = [years_dict[y] for y in sorted(years_dict.keys())]

        # Latest year stats
        latest_year = sorted(years_dict.keys())[-1] if years_dict else '2022'
        latest_stat = years_dict[latest_year]

        # State average for benchmarking
        state_latest_recs = self.filter_records(state=matched_state, year=latest_year)
        state_total = sum(r['total_crimes'] for r in state_latest_recs)
        state_dist_count = len(set(r['district'] for r in state_latest_recs)) or 1
        state_avg = round(state_total / state_dist_count, 1)

        # Safety rating estimation based on ratio to state average
        ratio = latest_stat['total'] / (state_avg or 1)
        if ratio < 0.5:
            safety_level = "Low Incident Zone"
            safety_badge = "success"
        elif ratio < 1.0:
            safety_level = "Moderate Incidence"
            safety_badge = "info"
        elif ratio < 1.8:
            safety_level = "Elevated Incidence"
            safety_badge = "warning"
        else:
            safety_level = "High Incident Zone"
            safety_badge = "danger"

        return {
            'district': matched_district,
            'state': matched_state,
            'latest_year': latest_year,
            'latest_stat': latest_stat,
            'state_avg': state_avg,
            'safety_level': safety_level,
            'safety_badge': safety_badge,
            'timeline': timeline,
            'categories': {
                'violent': latest_stat['violent'],
                'women_children': latest_stat['women_children'],
                'property_economic': latest_stat['property_economic'],
                'public_safety': latest_stat['public_safety'],
                'public_order': latest_stat['public_order'],
            }
        }

    def get_table_data(self, state='Karnataka', year='2022', search='', sort_by='total', sort_order='desc', page=1, page_size=20):
        """Returns paginated district rows for the data explorer table."""
        recs = self.filter_records(state=state, year=year)
        agg = {}

        for r in recs:
            d = r['district']
            if d not in agg:
                agg[d] = {
                    'district': d,
                    'state': r['state'],
                    'year': r['year'],
                    'total': 0,
                    'violent': 0,
                    'women_children': 0,
                    'property_economic': 0,
                    'public_safety': 0,
                    'murder': 0,
                    'theft': 0,
                    'rape': 0
                }
            agg[d]['total'] += r['total_crimes']
            agg[d]['violent'] += r['categories']['violent']
            agg[d]['women_children'] += r['categories']['women_children']
            agg[d]['property_economic'] += r['categories']['property_economic']
            agg[d]['public_safety'] += r['categories']['public_safety']
            agg[d]['murder'] += r['key_metrics']['murder']
            agg[d]['theft'] += r['key_metrics']['theft']
            agg[d]['rape'] += r['key_metrics']['rape']

        rows = list(agg.values())

        # Search filter
        if search:
            s = search.lower().strip()
            rows = [r for r in rows if s in r['district'].lower() or s in r['state'].lower()]

        # Sorting
        valid_sort_keys = ['district', 'total', 'violent', 'women_children', 'property_economic', 'public_safety', 'murder', 'theft', 'rape']
        key = sort_by if sort_by in valid_sort_keys else 'total'
        reverse = (sort_order.lower() != 'asc')

        if key == 'district':
            rows.sort(key=lambda x: x['district'].lower(), reverse=reverse)
        else:
            rows.sort(key=lambda x: x[key], reverse=reverse)

        total_rows = len(rows)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_rows = rows[start:end]

        return {
            'total_rows': total_rows,
            'page': page,
            'page_size': page_size,
            'total_pages': max(1, (total_rows + page_size - 1) // page_size),
            'rows': paginated_rows
        }
