"""
Advanced Natural-Language Crime Analytics AI Engine for KCAVP.
Analyzes authentic 2016-2022 IPC records across ALL 38 districts in Karnataka.
Understands conversational questions, year-specific queries, multi-year comparisons,
statewide statistics, multi-district rankings, safety assessments, and trend trajectories.
"""

import re
from .data_engine import CrimeDataEngine, CRIME_HEAD_META, CATEGORY_NAMES, CATEGORY_COLORS

DISTRICT_ALIASES = {
    'bengaluru city': 'Bengaluru City',
    'bangalore city': 'Bengaluru City',
    'bangalore': 'Bengaluru City',
    'bengaluru': 'Bengaluru City',
    'blore': 'Bengaluru City',
    'bengaluru dist': 'Bengaluru District',
    'bengaluru district': 'Bengaluru District',
    'bangalore rural': 'Bengaluru District',
    'bangalore district': 'Bengaluru District',
    'mysuru city': 'Mysuru City',
    'mysore city': 'Mysuru City',
    'mysore': 'Mysuru City',
    'mysuru': 'Mysuru City',
    'mysuru district': 'Mysuru District',
    'mysore district': 'Mysuru District',
    'belagavi city': 'Belagavi City',
    'belgaum city': 'Belagavi City',
    'belagavi district': 'Belagavi District',
    'belgaum district': 'Belagavi District',
    'belagavi': 'Belagavi District',
    'belgaum': 'Belagavi District',
    'kalaburgi city': 'Kalaburgi City',
    'gulbarga city': 'Kalaburgi City',
    'kalaburgi': 'Kalaburgi',
    'kalaburagi': 'Kalaburgi',
    'gulbarga': 'Kalaburgi',
    'hubballi dharwad city': 'Hubballi Dharwad City',
    'hubballi dharwad': 'Hubballi Dharwad City',
    'hubli dharwad': 'Hubballi Dharwad City',
    'hubli': 'Hubballi Dharwad City',
    'hubballi': 'Hubballi Dharwad City',
    'mangaluru city': 'Mangaluru City',
    'mangalore city': 'Mangaluru City',
    'mangalore': 'Mangaluru City',
    'mangaluru': 'Mangaluru City',
    'bagalkot': 'Bagalkot',
    'bagalkote': 'Bagalkot',
    'ballari': 'Ballari',
    'bellary': 'Ballari',
    'bidar': 'Bidar',
    'chamarajnagar': 'Chamarajnagar',
    'chamarajanagar': 'Chamarajnagar',
    'chikkaballapura': 'Chikkaballapura',
    'chikkaballapur': 'Chikkaballapura',
    'chikkamagaluru': 'Chikkamagaluru',
    'chikmagalur': 'Chikkamagaluru',
    'chitradurga': 'Chitradurga',
    'dakshina kannada': 'Dakshina Kannada',
    'south canara': 'Dakshina Kannada',
    'dk': 'Dakshina Kannada',
    'davanagere': 'Davanagere',
    'davangere': 'Davanagere',
    'dharwad': 'Dharwad',
    'gadag': 'Gadag',
    'hassan': 'Hassan',
    'haveri': 'Haveri',
    'k.g.f.': 'K.G.F.',
    'k.g.f': 'K.G.F.',
    'kgf': 'K.G.F.',
    'kolar gold fields': 'K.G.F.',
    'k.railways': 'K.Railways',
    'railways': 'K.Railways',
    'railway': 'K.Railways',
    'kodagu': 'Kodagu',
    'coorg': 'Kodagu',
    'kolar': 'Kolar',
    'koppal': 'Koppal',
    'mandya': 'Mandya',
    'raichur': 'Raichur',
    'ramanagara': 'Ramanagara',
    'ramanagar': 'Ramanagara',
    'shimoga': 'Shimoga',
    'shivamogga': 'Shimoga',
    'tumakuru': 'Tumakuru',
    'tumkur': 'Tumakuru',
    'udupi': 'Udupi',
    'uttara kannada': 'Uttara Kannada',
    'north canara': 'Uttara Kannada',
    'uk': 'Uttara Kannada',
    'vijayanagara': 'Vijayanagara',
    'vijayanagar': 'Vijayanagara',
    'vijayapura': 'Vijayapura',
    'bijapur': 'Vijayapura',
    'yadgiri': 'Yadgiri',
    'yadgir': 'Yadgiri',
}

# Accurate phrases mapped to specific crime heads
CRIME_HEAD_PATTERNS = [
    (r'\b(attempt(?:ed)?\s+to\s+murder|attempt(?:ed)?\s+murder)\b', 'attempt_to_commit_murder'),
    (r'\b(culpable\s+homicide)\b', 'culpable_homicide_not_amounting_to_murder'),
    (r'\b(murder|murders|killing|killings|homicide|homicides)\b', 'murder'),
    (r'\b(attempt(?:ed)?\s+rape)\b', 'attempt_to_commit_rape'),
    (r'\b(rape|rapes|sexual\s+assault)\b', 'rape'),
    (r'\b(kidnap(?:ping)?|abduction|abduct(?:ed)?)\b', 'kidnapping_and_abduction'),
    (r'\b(dacoity|gang\s+robbery)\b', 'dacoity'),
    (r'\b(robbery|robberies)\b', 'robbery'),
    (r'\b(burglary|burglaries|criminal\s+trespass|trespass|house\s+breaking|break[\s-]in)\b', 'criminal_trespass_or_burglary'),
    (r'\b(theft|thefts|stealing|stolen|vehicle\s+theft)\b', 'theft'),
    (r'\b(unlawful\s+assembly)\b', 'unlawful_assembly'),
    (r'\b(riot|riots|rioting|communal\s+clash(?:es)?)\b', 'riots'),
    (r'\b(breach\s+of\s+trust)\b', 'criminal_breach_of_trust'),
    (r'\b(cheating|fraud|scam|scams|financial\s+fraud)\b', 'cheating'),
    (r'\b(forgery|fake\s+documents)\b', 'forgery'),
    (r'\b(counterfeiting|fake\s+currency|counterfeit)\b', 'counterfeiting'),
    (r'\b(arson|setting\s+fire)\b', 'arson'),
    (r'\b(grievous\s+hurt|severe\s+hurt|serious\s+injury)\b', 'grievous_hurt'),
    (r'\b(dowry\s+death(?:s)?|dowry)\b', 'dowry_deaths'),
    (r'\b(assault\s+on\s+women|outrage\s+modesty|molestation|eve\s+teasing)\b', 'assault_on_women'),
    (r'\b(insult\s+to\s+modesty|modesty\s+insult)\b', 'insult_to_the_modesty_of_women'),
    (r'\b(cruelty\s+by\s+husband|498a|domestic\s+violence|domestic\s+cruelty)\b', 'cruelty_by_husband_or_his_relatives'),
    (r'\b(human\s+trafficking|trafficking)\b', 'human_trafficking'),
    (r'\b(death\s+by\s+negligence|negligence\s+death|negligent\s+death)\b', 'causing_death_by_negligence'),
    (r'\b(rash\s+driving|traffic\s+accident(?:s)?|road\s+accident(?:s)?|vehicle\s+accident(?:s)?|hit\s+and\s+run)\b', 'incidence_of_rash_driving'),
    (r'\b(extortion|blackmail|ransom)\b', 'extortion'),
    (r'\b(other\s+ipc|other\s+crimes|unclassified\s+crimes)\b', 'other_ipc_crimes'),
]

CATEGORY_PATTERNS = [
    (r'\b(violent\s+crime(?:s)?|violence|violent\s+offence(?:s)?)\b', 'violent'),
    (r'\b(crime(?:s)?\s+against\s+women|women\s+(?:and|&)\s+child(?:ren)?|women\s+safety|safety\s+of\s+women|women\s+crimes?|crimes?\s+on\s+women|female\s+safety)\b', 'women_children'),
    (r'\b(property\s+crime(?:s)?|economic\s+crime(?:s)?|financial\s+crime(?:s)?|property\s+(?:and|&)\s+economic)\b', 'property_economic'),
    (r'\b(public\s+safety|traffic\s+offence(?:s)?|road\s+safety)\b', 'public_safety'),
    (r'\b(public\s+order|law\s+and\s+order|communal\s+unrest)\b', 'public_order'),
]


def format_num(val):
    return f"{int(val):,}"


class CrimeChatbotEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.engine = CrimeDataEngine.get_instance()
        self.all_districts = self.engine.get_districts()
        self.years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']

    def _extract_districts(self, query):
        """Extracts any explicitly mentioned district names from the query."""
        q = query.lower()
        found = []
        sorted_aliases = sorted(DISTRICT_ALIASES.keys(), key=lambda x: len(x), reverse=True)
        matched_canonical = set()

        for alias in sorted_aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, q):
                canonical = DISTRICT_ALIASES[alias]
                if canonical not in matched_canonical:
                    matched_canonical.add(canonical)
                    found.append(canonical)

        return found

    def _extract_years(self, query):
        """Extracts all explicit or relative years mentioned in the query."""
        q = query.lower()
        found_years = []

        # Numerical years
        for y in self.years:
            if re.search(r'\b' + y + r'\b', q):
                found_years.append(y)

        # Relative year expressions
        if not found_years:
            if re.search(r'\b(latest|recent|most recent|current year)\b', q):
                found_years.append('2022')
            elif re.search(r'\b(lockdown|covid|pandemic)\b', q):
                found_years.append('2020')
            elif re.search(r'\b(baseline|earliest|initial year|start)\b', q):
                found_years.append('2016')

        return found_years

    def _extract_crime_head(self, query):
        """Extracts specific IPC crime head using rigorous regex patterns."""
        q = query.lower()
        for pattern, head_key in CRIME_HEAD_PATTERNS:
            if re.search(pattern, q):
                return head_key
        return None

    def _extract_category(self, query):
        """Extracts crime category using regex patterns."""
        q = query.lower()
        for pattern, cat_key in CATEGORY_PATTERNS:
            if re.search(pattern, q):
                return cat_key
        return None

    def _extract_direction(self, query):
        """Detects if query asks for highest vs lowest / safest."""
        q = query.lower()
        high_patterns = [
            r'\b(highest|most|top|maximum|max|worst|peak|leading|largest|higher|more|greater)\b',
            r'\b(highest crime|most crime|high crime|more crime|higher crime)\b'
        ]
        low_patterns = [
            r'\b(lowest|least|safest|safe|safety|minimum|min|best|less|lesser|fewer|fewest|lower|low)\b',
            r'\b(safest district|least crime|lowest crime|most peaceful|peaceful|less crime|lower crime|fewer crimes|fewest crimes)\b'
        ]

        for p in low_patterns:
            if re.search(p, q):
                return 'lowest'
        for p in high_patterns:
            if re.search(p, q):
                return 'highest'
        return None

    def _extract_limit(self, query):
        """Extracts ranking count (e.g. top 5, top 10, 3 safest)."""
        q = query.lower()
        match1 = re.search(r'\b(?:top|bottom|first|last|safest|highest|lowest)\s*(\d{1,2})\b', q)
        if match1:
            try:
                val = int(match1.group(1))
                return max(1, min(val, 38))
            except ValueError:
                pass
        match2 = re.search(r'\b(\d{1,2})\s*(?:top|bottom|first|last|safest|highest|lowest|districts)\b', q)
        if match2:
            try:
                val = int(match2.group(1))
                return max(1, min(val, 38))
            except ValueError:
                pass
        return 5

    def _is_year_superlative(self, query):
        """Checks if asking which YEAR was highest/lowest."""
        q = query.lower()
        patterns = [
            r'\bwhich\s+year\b',
            r'\bwhat\s+year\b',
            r'\byear\s+(?:with|has|had|recorded|saw)\s+(?:the\s+)?(?:highest|most|lowest|least|peak|less|fewer|lower|min|max|more)\b',
            r'\b(?:highest|worst|safest|lowest|peak|least|best)\s+year\b'
        ]
        return any(re.search(p, q) for p in patterns)

    def _is_trend_query(self, query):
        """Checks if query is asking about historical trend or trajectory."""
        q = query.lower()
        patterns = [
            r'\b(trend|trends|trending|trajectory|growth|timeline|progression|historical|over time|progression)\b',
            r'\b(increas(?:ing|ed)?|decreas(?:ing|ed)?|going up|going down)\b',
            r'\bfrom\s+2016\s+to\s+2022\b'
        ]
        return any(re.search(p, q) for p in patterns)

    def _is_pinned_query(self, query):
        """Checks if query is about pinned watch deck district."""
        q = query.lower()
        return any(w in q for w in ['pinned', 'preferred', 'track', 'watch deck', 'my district', 'star'])

    def _is_district_ranking_query(self, query):
        """Checks if user is asking to rank or find leader district."""
        q = query.lower()
        patterns = [
            r'\bwhich\s+district\b',
            r'\bwhat\s+district\b',
            r'\bwhich\s+city\b',
            r'\bwhere\s+(?:is|are|do)\s+(?:most|highest|least|lowest)\b',
            r'\b(safest|highest|lowest|top|bottom)\s+district\b',
            r'\bdistrict(?:s)?\s+with\s+(?:the\s+)?(?:most|highest|least|lowest)\b',
            r'\bwho\s+has\s+(?:the\s+)?(?:most|highest|least|lowest)\b'
        ]
        return any(re.search(p, q) for p in patterns)

    def _is_generic_crime_question(self, query):
        """Checks if query asks about overall crime count rather than a specific offense."""
        q = query.lower()
        patterns = [
            r'\bhow\s+many\s+crimes\b',
            r'\btotal\s+crime(?:s)?\b',
            r'\bcrime\s+statistics\b',
            r'\bcrime\s+count\b',
            r'\bnumber\s+of\s+crimes\b',
            r'\boverall\s+crime(?:s)?\b',
            r'\bcrimes?\s+in\s+20\d\d\b',
            r'\b20\d\d\s+crimes?\b'
        ]
        return any(re.search(p, q) for p in patterns)

    def ask(self, query, selected_district='Bengaluru City', selected_year='all', pinned_district=None):
        """
        Main natural-language intelligence dispatch.
        Understands intent conversationally and analyzes all 38 Karnataka districts.
        """
        if not query or not query.strip():
            return {
                'status': 'error',
                'title': 'Empty Query',
                'answer_html': '<p>Please enter a question to analyze Karnataka crime data.</p>',
                'suggestions': self._get_default_suggestions()
            }

        q = query.strip()
        districts = self._extract_districts(q)
        years = self._extract_years(q)
        crime_head = self._extract_crime_head(q)
        category = self._extract_category(q)
        direction = self._extract_direction(q)
        limit = self._extract_limit(q)

        # 1. Pinned District Watch-Deck Query
        if self._is_pinned_query(q):
            target_pinned = pinned_district or selected_district
            return self._handle_pinned_query(target_pinned)

        # 2. Year Superlative: e.g. "Which year had the highest crime?" / "Safest year"
        if self._is_year_superlative(q):
            dir_to_use = direction or 'highest'
            return self._handle_year_superlative(dir_to_use, crime_head, category)

        # 3. Two-Years Comparison: e.g. "Compare 2016 and 2022" / "2020 vs 2022"
        if len(years) >= 2:
            target_dist = districts[0] if districts else None
            return self._handle_two_years_comparison(years[0], years[1], target_dist, crime_head, category)

        # 4. Multi-District Comparison: e.g. "Compare Bengaluru and Mysuru"
        if len(districts) >= 2 or ('compare' in q.lower() and len(districts) == 1):
            dist_a = districts[0]
            dist_b = districts[1] if len(districts) >= 2 else (selected_district if selected_district != dist_a else 'Mysuru City')
            target_yr = years[0] if years else selected_year
            return self._handle_comparison(dist_a, dist_b, target_yr, crime_head, category)

        # 5. All-District Ranking: e.g. "Which district has highest crime?", "Safest district in Karnataka", "Top 5 districts in 2022"
        if self._is_district_ranking_query(q) or (direction and not districts):
            target_yr = years[0] if years else selected_year
            dir_to_use = direction or 'highest'
            metric_key = crime_head or category or 'total'
            metric_type = 'head' if crime_head else ('category' if category else 'total')
            return self._handle_all_districts_ranking(dir_to_use, metric_key, metric_type, target_yr, limit, selected_district)

        # 6. Specific District + Specific Year (e.g. "Crime in Bengaluru in 2021", "Murders in Belagavi in 2020")
        if districts and years:
            return self._handle_district_year(districts[0], years[0], crime_head, category)

        # 7. Specific District across All Years (e.g. "Crime in Tumakuru", "Thefts in Mandya")
        if districts:
            target_yr = selected_year
            return self._handle_district_analysis(districts[0], target_yr, crime_head, category)

        # 8. Specific Year Queries (Statewide, NO District mentioned):
        # E.g. "How many crimes in 2022?", "Total crime in 2020", "Murders in 2019", "2021 statistics"
        if years:
            target_yr = years[0]
            if crime_head or category:
                # E.g. "How many murders in 2022?" or "Thefts in 2020" or "Violent crimes in 2021"
                return self._handle_year_offense_statewide(target_yr, crime_head, category, selected_district)
            else:
                # E.g. "How many crimes in 2022?" or "2020 crime rate" or "Total crime in 2021"
                return self._handle_year_overview(target_yr, selected_district)

        # 9. Historical Trend query
        if self._is_trend_query(q):
            target_dist = selected_district if any(w in q.lower() for w in ['here', 'this district', 'current']) else None
            return self._handle_trend(target_dist, crime_head, category)

        # 10. Specific Offense / Category across all of Karnataka (no year specified)
        # E.g. "Total murders in Karnataka", "How many thefts across Karnataka?"
        if (crime_head or category) and any(w in q.lower() for w in ['karnataka', 'statewide', 'across', 'total', 'overall', 'state']):
            return self._handle_statewide(selected_year, crime_head, category)

        # 11. Generic statewide question across all 38 districts
        # E.g. "Total crimes in Karnataka", "Overall crime rate"
        if any(w in q.lower() for w in ['karnataka', 'statewide', 'overall', 'whole state', 'all districts']):
            return self._handle_statewide(selected_year, None, None)

        # 12. Question about current selected district (e.g. "What is top offense?", "Violent crimes")
        if crime_head or category:
            return self._handle_district_analysis(selected_district, selected_year, crime_head, category)

        if any(w in q.lower() for w in ['top offense', 'highest offense', 'what crime', 'crime breakdown', 'status', 'summary', 'overview']):
            return self._handle_district_analysis(selected_district, selected_year, None, None)

        # 13. Conversational Fallback with actual datasets
        return self._handle_conversational_fallback(q, selected_district, selected_year)

    # =========================================================================
    # CORE HANDLERS
    # =========================================================================

    def _handle_year_overview(self, year, current_district=None):
        """Handles queries like 'How many crimes in 2022?' or 'Total crime in 2020' across Karnataka."""
        records = [self.engine.records_by_district_year.get((d.lower(), year), {}) for d in self.all_districts]
        state_total = sum(r.get('total_crimes', 0) for r in records)
        state_cats = {c: sum(r.get('categories', {}).get(c, 0) for r in records) for c in CATEGORY_NAMES}

        # Calculate YoY vs previous year
        yoy_str = ""
        prev_yr_idx = self.years.index(year) - 1 if year in self.years else -1
        if prev_yr_idx >= 0:
            prev_year = self.years[prev_yr_idx]
            prev_records = [self.engine.records_by_district_year.get((d.lower(), prev_year), {}) for d in self.all_districts]
            prev_total = sum(r.get('total_crimes', 0) for r in prev_records)
            if prev_total > 0:
                diff_pct = round(((state_total - prev_total) / prev_total) * 100, 1)
                sign = "+" if diff_pct > 0 else ""
                color = "#f43f5e" if diff_pct > 0 else "#10b981"
                yoy_str = f" <span style='font-size: 12px; color: {color}; font-weight: 600;'>({sign}{diff_pct}% vs {prev_year})</span>"

        # District rankings in this year
        dist_tots = [(d, self.engine.records_by_district_year.get((d.lower(), year), {}).get('total_crimes', 0)) for d in self.all_districts]
        dist_tots.sort(key=lambda x: x[1], reverse=True)
        top5 = dist_tots[:5]
        safe3 = dist_tots[-3:]

        # Current district callout if available
        curr_callout = ""
        if current_district:
            c_rec = self.engine.records_by_district_year.get((current_district.lower(), year), {})
            c_val = c_rec.get('total_crimes', 0)
            c_rank = next((i + 1 for i, item in enumerate(dist_tots) if item[0] == current_district), 1)
            c_share = round((c_val / max(1, state_total)) * 100, 1)
            curr_callout = f"""
            <div style="margin-top: 10px; padding: 8px 12px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); border-radius: 4px; font-size: 12px; color: var(--text-muted);">
                📍 <strong>Your Selected Dashboard District ({current_district}) in {year}:</strong> recorded <strong style="color: #fff;">{format_num(c_val)}</strong> crimes, ranking <strong style="color: #38bdf8;">#{c_rank} of 38</strong> districts ({c_share}% of state total).
            </div>
            """

        top5_rows = "".join([
            f"<div style='display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
            f"<span>#{i+1} <button class='kcavp-chat-switch-btn' data-district='{d}' style='background:none;border:none;color:#f8fafc;font-weight:600;cursor:pointer;text-decoration:underline dotted;'>{d}</button></span>"
            f"<strong style='color:#fff;'>{format_num(val)} cases ({round((val/max(1, state_total))*100, 1)}%)</strong>"
            f"</div>"
            for i, (d, val) in enumerate(top5)
        ])

        cat_pills = "".join([
            f"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:6px 8px;'>"
            f"<div style='font-size:11px; color:var(--text-muted);'>{label}</div>"
            f"<div style='font-size:13.5px; font-weight:700; color:{CATEGORY_COLORS.get(cat, '#fff')};'>{format_num(cnt)}</div>"
            f"<div style='font-size:10px; color:var(--text-faint);'>{round((cnt/max(1, state_total))*100, 1)}% of year</div>"
            f"</div>"
            for cat, label in CATEGORY_NAMES.items()
            for cnt in [state_cats.get(cat, 0)]
        ])

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            📅 In <strong>{year}</strong>, a total of <strong style="color: #fff; font-size: 16px;">{format_num(state_total)} IPC crimes</strong> were recorded across all <strong>38 districts of Karnataka</strong>{yoy_str}.<br>
            • <strong>Highest Crime District</strong>: <strong>{top5[0][0]}</strong> ({format_num(top5[0][1])} cases, {round((top5[0][1]/max(1, state_total))*100, 1)}% of state).<br>
            • <strong>Safest District</strong>: <strong>{safe3[-1][0]}</strong> ({format_num(safe3[-1][1])} cases).
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0;">
            {cat_pills}
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
            <div style="font-weight: 700; color: #38bdf8; font-size: 12px; margin-bottom: 6px;">Top 5 Contributing Districts in {year}:</div>
            {top5_rows}
        </div>
        {curr_callout}
        """

        title = f"📅 Karnataka Statewide Crime Intelligence ({year})"
        summary_text = f"In {year}, Karnataka recorded {format_num(state_total)} total IPC crimes across all 38 districts."

        return {
            'status': 'ok',
            'intent': 'year_overview',
            'year': year,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': [
                f"Which district has most murders in {year}?",
                f"Safest district in {year}",
                f"Compare {year} and 2016",
                "How have crimes trended from 2016 to 2022?"
            ]
        }

    def _handle_year_offense_statewide(self, year, crime_head, category, current_district=None):
        """Handles queries like 'How many murders in 2022?' or 'Thefts in 2020' across Karnataka."""
        records = [self.engine.records_by_district_year.get((d.lower(), year), {}) for d in self.all_districts]
        state_total_crimes = sum(r.get('total_crimes', 0) for r in records)

        if crime_head:
            meta = CRIME_HEAD_META.get(crime_head, {'name': crime_head.replace('_', ' ').title(), 'icon': '⚔️'})
            metric_label = meta['name']
            icon = meta['icon']
            head_counts = [(d, self.engine.records_by_district_year.get((d.lower(), year), {}).get('crimes', {}).get(crime_head, 0)) for d in self.all_districts]
        else:
            cat_label = CATEGORY_NAMES.get(category, category.title())
            metric_label = cat_label
            icon = '🛡️'
            head_counts = [(d, self.engine.records_by_district_year.get((d.lower(), year), {}).get('categories', {}).get(category, 0)) for d in self.all_districts]

        total_offense = sum(item[1] for item in head_counts)
        pct_of_all = round((total_offense / max(1, state_total_crimes)) * 100, 1)

        head_counts.sort(key=lambda x: x[1], reverse=True)
        top5 = head_counts[:5]

        # YoY change for this offense
        yoy_str = ""
        prev_yr_idx = self.years.index(year) - 1 if year in self.years else -1
        if prev_yr_idx >= 0:
            prev_year = self.years[prev_yr_idx]
            if crime_head:
                prev_offense_tot = sum(self.engine.records_by_district_year.get((d.lower(), prev_year), {}).get('crimes', {}).get(crime_head, 0) for d in self.all_districts)
            else:
                prev_offense_tot = sum(self.engine.records_by_district_year.get((d.lower(), prev_year), {}).get('categories', {}).get(category, 0) for d in self.all_districts)
            if prev_offense_tot > 0:
                diff_pct = round(((total_offense - prev_offense_tot) / prev_offense_tot) * 100, 1)
                sign = "+" if diff_pct > 0 else ""
                color = "#f43f5e" if diff_pct > 0 else "#10b981"
                yoy_str = f" <span style='font-size: 12px; color: {color}; font-weight: 600;'>({sign}{diff_pct}% vs {prev_year})</span>"

        curr_callout = ""
        if current_district:
            c_val = next((item[1] for item in head_counts if item[0] == current_district), 0)
            c_rank = next((i + 1 for i, item in enumerate(head_counts) if item[0] == current_district), 1)
            curr_callout = f"""
            <div style="margin-top: 10px; padding: 8px 12px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); border-radius: 4px; font-size: 12px; color: var(--text-muted);">
                📍 <strong>Your Selected Dashboard District ({current_district}) in {year}:</strong> recorded <strong style="color: #fff;">{format_num(c_val)}</strong> {metric_label.lower()}, ranking <strong style="color: #38bdf8;">#{c_rank} of 38</strong> districts in Karnataka ({round((c_val/max(1, total_offense))*100, 1)}% of statewide {metric_label.lower()}).
            </div>
            """

        top5_rows = "".join([
            f"<div style='display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
            f"<span>#{i+1} <button class='kcavp-chat-switch-btn' data-district='{d}' style='background:none;border:none;color:#f8fafc;font-weight:600;cursor:pointer;text-decoration:underline dotted;'>{d}</button></span>"
            f"<strong style='color:#fff;'>{format_num(cnt)} cases ({round((cnt/max(1, total_offense))*100, 1)}%)</strong>"
            f"</div>"
            for i, (d, cnt) in enumerate(top5)
        ])

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            {icon} In <strong>{year}</strong>, there were <strong style="color: #fff; font-size: 16px;">{format_num(total_offense)} {metric_label}</strong> cases recorded across Karnataka{yoy_str}.<br>
            • Represents <strong>{pct_of_all}%</strong> of all {format_num(state_total_crimes)} IPC incidents recorded in {year}.<br>
            • <strong>Leading District</strong>: <strong>{top5[0][0]}</strong> accounts for <strong>{format_num(top5[0][1])}</strong> cases ({round((top5[0][1]/max(1, total_offense))*100, 1)}% of all {metric_label.lower()} in the state).
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
            <div style="font-weight: 700; color: #38bdf8; font-size: 12px; margin-bottom: 6px;">Top Contributing Districts for {metric_label} in {year}:</div>
            {top5_rows}
        </div>
        {curr_callout}
        """

        title = f"{icon} Karnataka Statewide: {metric_label} ({year})"
        summary_text = f"In {year}, Karnataka recorded {format_num(total_offense)} {metric_label} cases."

        return {
            'status': 'ok',
            'intent': 'year_offense_statewide',
            'year': year,
            'metric': crime_head or category,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': [
                f"Which district has highest {metric_label.lower()} in {year}?",
                f"Total {metric_label.lower()} across all years",
                f"Safest district in {year}",
                f"Compare {year} and 2016"
            ]
        }

    def _handle_district_year(self, district, year, crime_head, category):
        """Handles queries for a specific district in a specific year, e.g., 'Crime in Bengaluru in 2021'."""
        r = self.engine.get_record(district, year=year)
        sum_data = self.engine.get_district_summary(district, year=year)

        # Compute rank of this district in this year across all 38 districts
        dist_tots = [(d, self.engine.records_by_district_year.get((d.lower(), year), {}).get('total_crimes', 0)) for d in self.all_districts]
        dist_tots.sort(key=lambda x: x[1], reverse=True)
        dist_rank = next((i + 1 for i, item in enumerate(dist_tots) if item[0] == district), 1)

        state_total_yr = sum(item[1] for item in dist_tots)
        state_share = round((r['total_crimes'] / max(1, state_total_yr)) * 100, 1)

        if crime_head:
            meta = CRIME_HEAD_META.get(crime_head, {'name': crime_head.replace('_', ' ').title(), 'icon': '📌'})
            head_cnt = r['crimes'].get(crime_head, 0)
            head_pct = round((head_cnt / max(1, r['total_crimes'])) * 100, 1)

            # State ranking for this offense in this year
            offense_ranks = [(d, self.engine.records_by_district_year.get((d.lower(), year), {}).get('crimes', {}).get(crime_head, 0)) for d in self.all_districts]
            offense_ranks.sort(key=lambda x: x[1], reverse=True)
            offense_rank = next((i + 1 for i, item in enumerate(offense_ranks) if item[0] == district), 1)
            state_offense_tot = sum(item[1] for item in offense_ranks)

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                {meta['icon']} In <strong>{district}</strong> during <strong>{year}</strong>, recorded <strong>{meta['name']}</strong> stood at <strong style="color: #fff; font-size: 15px;">{format_num(head_cnt)} cases</strong>.<br>
                • Represents <strong>{head_pct}%</strong> of all crimes in this district in {year}.<br>
                • Ranks <strong style="color: #38bdf8;">#{offense_rank} of 38</strong> districts in Karnataka for this offense ({round((head_cnt/max(1, state_offense_tot))*100, 1)}% of Karnataka's total {format_num(state_offense_tot)} cases).
            </div>
            <div style="margin-top: 8px;">
                <button class="kcavp-chat-switch-btn btn-primary" data-district="{district}" style="padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer;">
                    View {district} in Dashboard →
                </button>
            </div>
            """
            title = f"{meta['icon']} {district}: {meta['name']} in {year}"
            summary_text = f"In {year}, {district} recorded {format_num(head_cnt)} {meta['name']} cases (Rank #{offense_rank} in Karnataka)."
        else:
            top_off = sum_data['top_offense']
            yoy_growth = sum_data.get('yoy_growth', 0.0)
            sign = "+" if yoy_growth > 0 else ""
            color = "#f43f5e" if yoy_growth > 0 else "#10b981"
            yoy_display = f" <span style='color:{color}; font-weight:600;'>({sign}{yoy_growth}% vs {sum_data.get('prev_year')})</span>" if sum_data.get('prev_year') else ""

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                📍 In <strong>{district}</strong> during <strong>{year}</strong>, total recorded IPC crimes stood at <strong style="color: #fff; font-size: 16px;">{format_num(r['total_crimes'])} cases</strong>{yoy_display}.<br>
                • Ranked <strong style="color: #38bdf8;">#{dist_rank} of 38</strong> districts in Karnataka ({state_share}% of Karnataka's total {format_num(state_total_yr)} crimes in {year}).<br>
                • Primary threat: <strong>{top_off['name']}</strong> ({format_num(top_off['count'])} cases, {top_off['percentage']}% share).
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0; font-size: 12px;">
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Violent:</span><br>
                    <strong style="color: #f43f5e;">{format_num(r['categories']['violent'])}</strong> ({sum_data['category_percentages']['violent']}%)
                </div>
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Property/Theft:</span><br>
                    <strong style="color: #60a5fa;">{format_num(r['categories']['property_economic'])}</strong> ({sum_data['category_percentages']['property_economic']}%)
                </div>
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Women/Children:</span><br>
                    <strong style="color: #ec4899;">{format_num(r['categories']['women_children'])}</strong> ({sum_data['category_percentages']['women_children']}%)
                </div>
            </div>
            <div style="margin-top: 8px;">
                <button class="kcavp-chat-switch-btn btn-primary" data-district="{district}" style="padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer;">
                    View {district} in Dashboard →
                </button>
            </div>
            """
            title = f"📍 {district} Crime Profile ({year})"
            summary_text = f"In {year}, {district} recorded {format_num(r['total_crimes'])} crimes (Rank #{dist_rank} in Karnataka)."

        return {
            'status': 'ok',
            'intent': 'district_year',
            'district': district,
            'year': year,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'highlight_district': district,
            'suggestions': [
                f"Violent crimes in {district} in {year}",
                f"Thefts in {district} in {year}",
                f"Compare {district} and Bengaluru City",
                f"Total crime in Karnataka in {year}"
            ]
        }

    def _handle_year_superlative(self, direction, crime_head, category):
        """Answers queries like 'Which year had the highest crime?' or 'Safest year'."""
        timeline = []
        for y in self.years:
            records = [self.engine.records_by_district_year.get((d.lower(), y), {}) for d in self.all_districts]
            if crime_head:
                tot = sum(r.get('crimes', {}).get(crime_head, 0) for r in records)
            elif category:
                tot = sum(r.get('categories', {}).get(category, 0) for r in records)
            else:
                tot = sum(r.get('total_crimes', 0) for r in records)
            timeline.append({'year': y, 'total': tot})

        metric_label = CRIME_HEAD_META.get(crime_head, {}).get('name') if crime_head else (CATEGORY_NAMES.get(category, category) if category else "Total IPC Crimes")

        reverse = (direction == 'highest')
        timeline_sorted = sorted(timeline, key=lambda x: x['total'], reverse=reverse)
        lead_year = timeline_sorted[0]

        rows_html = "".join([
            f"<div style='display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
            f"<span>Year {item['year']}</span>"
            f"<strong style='color:#fff;'>{format_num(item['total'])} cases</strong>"
            f"</div>"
            for item in sorted(timeline, key=lambda x: x['year'])
        ])

        if direction == 'highest':
            action = f"Highest {metric_label}"
            takeaway = f"<strong>{lead_year['year']}</strong> recorded the highest volume with <strong>{format_num(lead_year['total'])} cases</strong>."
        else:
            action = f"Lowest / Safest Year for {metric_label}"
            takeaway = f"<strong>{lead_year['year']}</strong> was the lowest / safest year with <strong>{format_num(lead_year['total'])} cases</strong> (reflecting COVID-19 mobility curbs in 2020)."

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            📊 <strong>{action}:</strong><br>
            {takeaway}
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
            <div style="font-weight: 700; color: #38bdf8; font-size: 12px; margin-bottom: 6px;">7-Year Historical Timeline (2016–2022):</div>
            {rows_html}
        </div>
        """

        title = f"📊 Historical Analysis: {action}"
        summary_text = f"{lead_year['year']} had the {direction} {metric_label} ({format_num(lead_year['total'])})."

        return {
            'status': 'ok',
            'intent': 'year_superlative',
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': [
                "How many crimes in 2022?",
                "Total crime in 2020",
                "Which district has highest crime?",
                "Safest district in Karnataka"
            ]
        }

    def _handle_two_years_comparison(self, year_a, year_b, district=None, crime_head=None, category=None):
        """Compares two years side-by-side, either statewide or for a district."""
        if district:
            rec_a = self.engine.get_record(district, year=year_a)
            rec_b = self.engine.get_record(district, year=year_b)
            tot_a = rec_a['total_crimes']
            tot_b = rec_b['total_crimes']
            context_title = f"{district}: {year_a} vs {year_b}"
        else:
            records_a = [self.engine.records_by_district_year.get((d.lower(), year_a), {}) for d in self.all_districts]
            records_b = [self.engine.records_by_district_year.get((d.lower(), year_b), {}) for d in self.all_districts]
            tot_a = sum(r.get('total_crimes', 0) for r in records_a)
            tot_b = sum(r.get('total_crimes', 0) for r in records_b)
            context_title = f"Karnataka Statewide: {year_a} vs {year_b}"

        diff = tot_b - tot_a
        diff_pct = round((diff / max(1, tot_a)) * 100, 1)
        sign = "+" if diff > 0 else ""
        color = "#f43f5e" if diff > 0 else "#10b981"

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            ⚖️ <strong>Comparative Timeline ({context_title}):</strong><br>
            • <strong>Year {year_a}</strong>: <strong style="color: #fff;">{format_num(tot_a)}</strong> cases<br>
            • <strong>Year {year_b}</strong>: <strong style="color: #fff;">{format_num(tot_b)}</strong> cases<br>
            Net Shift: <strong style="color: {color};">{sign}{format_num(diff)} cases ({sign}{diff_pct}%)</strong> from {year_a} to {year_b}.
        </div>
        """

        title = f"⚖️ Comparative Timeline: {context_title}"
        summary_text = f"{year_a} ({format_num(tot_a)}) vs {year_b} ({format_num(tot_b)}): {sign}{diff_pct}% change."

        return {
            'status': 'ok',
            'intent': 'two_years_comparison',
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': [
                f"How many crimes in {year_b}?",
                "Which district has highest crime?",
                "Safest district in Karnataka"
            ]
        }

    def _handle_all_districts_ranking(self, direction, metric_key, metric_type, year, limit, current_district):
        """Ranks all 38 districts by total crimes, category, or specific crime head."""
        year_str = "2016–2022 (Combined)" if year in ['all', 'combined'] else f"Year {year}"
        rankings = []

        if metric_type == 'head':
            meta = CRIME_HEAD_META.get(metric_key, {'name': metric_key.replace('_', ' ').title(), 'icon': '⚔️', 'category': 'violent'})
            metric_label = meta['name']
            icon = meta['icon']
        elif metric_type == 'category':
            metric_label = CATEGORY_NAMES.get(metric_key, metric_key.replace('_', ' ').title())
            icon = '📁'
        else:
            metric_label = 'Total IPC Crimes'
            icon = '📊'

        state_total = 0
        for d in self.all_districts:
            r = self.engine.get_record(d, year=year)
            if metric_type == 'head':
                val = r['crimes'].get(metric_key, 0)
            elif metric_type == 'category':
                val = r['categories'].get(metric_key, 0)
            else:
                val = r['total_crimes']
            rankings.append({'district': d, 'value': val})
            state_total += val

        reverse = (direction == 'highest')
        rankings.sort(key=lambda x: x['value'], reverse=reverse)

        top_leader = rankings[0]
        state_avg = round(state_total / len(self.all_districts)) if self.all_districts else 0

        current_rank = next((i + 1 for i, r in enumerate(rankings) if r['district'] == current_district), None)
        current_val = next((r['value'] for r in rankings if r['district'] == current_district), 0)

        if direction == 'highest':
            title_icon = "🏆"
            action_desc = f"Highest Recorded {metric_label}"
            takeaway = f"<strong>{top_leader['district']}</strong> records the highest incidence with <strong>{format_num(top_leader['value'])}</strong> cases ({round((top_leader['value'] / max(1, state_total)) * 100, 1)}% of the Karnataka total)."
        else:
            title_icon = "🛡️"
            action_desc = f"Safest / Lowest {metric_label}"
            takeaway = f"<strong>{top_leader['district']}</strong> is the safest with lowest {metric_label.lower()}, recording only <strong>{format_num(top_leader['value'])}</strong> cases."

        title = f"{title_icon} All-District Analysis: {action_desc} ({year_str})"

        rows_html = ""
        max_val = rankings[0]['value'] if rankings[0]['value'] > 0 else 1
        for i, item in enumerate(rankings[:limit]):
            rank = i + 1
            pct_of_state = round((item['value'] / max(1, state_total)) * 100, 1)
            bar_width = max(4, round((item['value'] / max_val) * 100))
            is_active = (item['district'] == current_district)
            active_badge = ' <span style="font-size: 10px; background: rgba(99, 102, 241, 0.25); color: #818cf8; padding: 2px 6px; border-radius: 4px; font-weight: 600;">Current View</span>' if is_active else ''

            color_class = "#f43f5e" if direction == 'highest' and rank == 1 else ("#10b981" if direction == 'lowest' and rank == 1 else "#38bdf8")

            rows_html += f"""
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 12.5px;">
                <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                    <span style="font-weight: 700; width: 22px; color: {color_class};">#{rank}</span>
                    <button class="kcavp-chat-switch-btn" data-district="{item['district']}" style="background: none; border: none; padding: 0; color: #f8fafc; font-weight: 600; cursor: pointer; text-align: left; text-decoration: underline dotted var(--accent-cyan); font-size: 13px;" title="Click to view {item['district']} on dashboard">
                        {item['district']}
                    </button>{active_badge}
                </div>
                <div style="width: 32%; margin: 0 10px; background: rgba(255, 255, 255, 0.05); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="width: {bar_width}%; height: 100%; background: {color_class}; border-radius: 3px;"></div>
                </div>
                <div style="text-align: right; min-width: 90px;">
                    <span style="font-weight: 700; color: #ffffff;">{format_num(item['value'])}</span>
                    <span style="color: var(--text-faint); font-size: 11px;"> ({pct_of_state}%)</span>
                </div>
            </div>
            """

        context_html = ""
        if current_district and current_district != top_leader['district']:
            context_html = f"""
            <div style="margin-top: 10px; padding: 8px 12px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); border-radius: 4px; font-size: 12px; color: var(--text-muted);">
                📍 <strong>Your Selected Dashboard District ({current_district})</strong> ranks <strong>#{current_rank}</strong> out of 38 districts with <strong>{format_num(current_val)}</strong> cases ({round((current_val/max(1, state_total))*100, 1)}% of Karnataka total).
            </div>
            """

        answer_html = f"""
        <div style="margin-bottom: 8px; line-height: 1.5; font-size: 13px; color: var(--text-main);">
            {icon} {takeaway}
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 8px; margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-faint); text-transform: uppercase; letter-spacing: 0.5px; padding: 4px 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                <span>Rank & District (38 Analyzed)</span>
                <span>Incident Count (% of State)</span>
            </div>
            {rows_html}
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11.5px; color: var(--text-muted); margin-top: 6px; padding: 0 4px;">
            <span>Statewide Total: <strong style="color: #fff;">{format_num(state_total)}</strong></span>
            <span>District Average: <strong style="color: #fff;">{format_num(state_avg)}</strong></span>
        </div>
        {context_html}
        """

        suggestions = [
            f"Safest districts for {metric_label.lower()}" if direction == 'highest' else f"Highest {metric_label.lower()} districts",
            f"Compare {top_leader['district']} and {current_district}",
            f"Total {metric_label.lower()} in Karnataka",
            "Top 5 districts overall"
        ]

        return {
            'status': 'ok',
            'intent': 'all_districts_ranking',
            'direction': direction,
            'metric': metric_key,
            'year': year,
            'title': title,
            'summary_text': f"{top_leader['district']} has the {direction} {metric_label} ({format_num(top_leader['value'])}).",
            'answer_html': answer_html,
            'top_district': top_leader['district'],
            'suggestions': suggestions
        }

    def _handle_comparison(self, dist_a, dist_b, year, crime_head, category):
        """Compares two districts side-by-side."""
        sum_a = self.engine.get_district_summary(dist_a, year=year)
        sum_b = self.engine.get_district_summary(dist_b, year=year)
        rec_a = self.engine.get_record(dist_a, year=year)
        rec_b = self.engine.get_record(dist_b, year=year)

        year_str = "2016–2022" if year in ['all', 'combined'] else year
        tot_a = sum_a['total_crimes']
        tot_b = sum_b['total_crimes']

        diff = abs(tot_a - tot_b)
        higher_dist = dist_a if tot_a >= tot_b else dist_b
        lower_dist = dist_b if tot_a >= tot_b else dist_a
        multiple = round(max(tot_a, tot_b) / max(1, min(tot_a, tot_b)), 1)

        specific_note = ""
        if crime_head:
            meta = CRIME_HEAD_META.get(crime_head, {'name': crime_head.replace('_', ' ').title()})
            cnt_a = rec_a['crimes'].get(crime_head, 0)
            cnt_b = rec_b['crimes'].get(crime_head, 0)
            specific_note = f"""
            <div style="background: rgba(56, 189, 248, 0.1); border-left: 3px solid #38bdf8; padding: 8px 12px; border-radius: 4px; margin: 8px 0; font-size: 12.5px;">
                🎯 <strong>{meta['name']} Focus:</strong><br>
                • <strong>{dist_a}</strong>: {format_num(cnt_a)} cases ({round((cnt_a/max(1, tot_a))*100, 1)}% of district)<br>
                • <strong>{dist_b}</strong>: {format_num(cnt_b)} cases ({round((cnt_b/max(1, tot_b))*100, 1)}% of district)
            </div>
            """

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.5; color: var(--text-main); margin-bottom: 10px;">
            ⚖️ <strong>Comparative Intelligence ({year_str}):</strong><br>
            <strong>{higher_dist}</strong> recorded <strong>{multiple}x</strong> more total crimes than <strong>{lower_dist}</strong> (a difference of <strong>{format_num(diff)}</strong> cases).
        </div>
        {specific_note}
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0;">
            <!-- Column A -->
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #60a5fa; font-size: 14px;">{dist_a}</strong>
                    <button class="kcavp-chat-switch-btn" data-district="{dist_a}" style="padding: 2px 8px; font-size: 11px; background: rgba(96, 165, 250, 0.15); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 4px; cursor: pointer;">View →</button>
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 6px;">{format_num(tot_a)}</div>
                <div style="font-size: 11.5px; color: var(--text-muted); line-height: 1.6;">
                    • Violent: <strong style="color: #fff;">{format_num(sum_a['categories']['violent'])}</strong> ({sum_a['category_percentages']['violent']}%)<br>
                    • Property/Theft: <strong style="color: #fff;">{format_num(sum_a['categories']['property_economic'])}</strong><br>
                    • Women & Children: <strong style="color: #fff;">{format_num(sum_a['categories']['women_children'])}</strong><br>
                    • Top Crime: <strong>{sum_a['top_offense']['name']}</strong> ({format_num(sum_a['top_offense']['count'])})
                </div>
            </div>
            <!-- Column B -->
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #ec4899; font-size: 14px;">{dist_b}</strong>
                    <button class="kcavp-chat-switch-btn" data-district="{dist_b}" style="padding: 2px 8px; font-size: 11px; background: rgba(236, 72, 153, 0.15); color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.3); border-radius: 4px; cursor: pointer;">View →</button>
                </div>
                <div style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 6px;">{format_num(tot_b)}</div>
                <div style="font-size: 11.5px; color: var(--text-muted); line-height: 1.6;">
                    • Violent: <strong style="color: #fff;">{format_num(sum_b['categories']['violent'])}</strong> ({sum_b['category_percentages']['violent']}%)<br>
                    • Property/Theft: <strong style="color: #fff;">{format_num(sum_b['categories']['property_economic'])}</strong><br>
                    • Women & Children: <strong style="color: #fff;">{format_num(sum_b['categories']['women_children'])}</strong><br>
                    • Top Crime: <strong>{sum_b['top_offense']['name']}</strong> ({format_num(sum_b['top_offense']['count'])})
                </div>
            </div>
        </div>
        """

        suggestions = [
            f"Violent crimes in {dist_a}",
            f"Violent crimes in {dist_b}",
            f"7-year trend in {dist_a}",
            "Top 5 districts overall"
        ]

        return {
            'status': 'ok',
            'intent': 'district_comparison',
            'districts': [dist_a, dist_b],
            'year': year,
            'title': f"⚖️ Comparative Profile: {dist_a} vs {dist_b} ({year_str})",
            'summary_text': f"{dist_a} ({format_num(tot_a)}) vs {dist_b} ({format_num(tot_b)}).",
            'answer_html': answer_html,
            'suggestions': suggestions
        }

    def _handle_statewide(self, year, crime_head, category):
        """Aggregates all 38 districts across 2016-2022 or a specified year."""
        year_str = "2016–2022 (7-Year Total)" if year in ['all', 'combined'] else f"Year {year}"

        state_total = 0
        state_categories = {c: 0 for c in CATEGORY_NAMES}
        district_counts = []
        state_crimes = {k: 0 for k in CRIME_HEAD_META}

        for d in self.all_districts:
            r = self.engine.get_record(d, year=year)
            state_total += r['total_crimes']
            for c, val in r['categories'].items():
                state_categories[c] = state_categories.get(c, 0) + val
            for k, val in r['crimes'].items():
                state_crimes[k] = state_crimes.get(k, 0) + val
            district_counts.append({'district': d, 'total': r['total_crimes']})

        district_counts.sort(key=lambda x: x['total'], reverse=True)
        top_contributor = district_counts[0]

        if crime_head:
            meta = CRIME_HEAD_META.get(crime_head, {'name': crime_head.replace('_', ' ').title(), 'icon': '⚔️'})
            head_total = state_crimes.get(crime_head, 0)
            pct_of_state = round((head_total / max(1, state_total)) * 100, 1)

            head_by_dist = []
            for d in self.all_districts:
                r = self.engine.get_record(d, year=year)
                head_by_dist.append({'district': d, 'count': r['crimes'].get(crime_head, 0)})
            head_by_dist.sort(key=lambda x: x['count'], reverse=True)
            top_h_dist = head_by_dist[0]

            rows_html = "".join([
                f"<div style='display:flex; justify-content:space-between; padding:5px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
                f"<span>#{i+1} <strong>{item['district']}</strong></span>"
                f"<span style='color:#fff;'><strong>{format_num(item['count'])}</strong> cases ({round((item['count']/max(1, head_total))*100, 1)}%)</span>"
                f"</div>"
                for i, item in enumerate(head_by_dist[:5])
            ])

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                {meta['icon']} Statewide recorded <strong>{meta['name']}</strong> across Karnataka ({year_str}) stands at <strong style="color: #fff; font-size: 15px;">{format_num(head_total)}</strong> cases ({pct_of_state}% of all {format_num(state_total)} IPC incidents).
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
                <div style="font-weight: 700; color: #38bdf8; font-size: 12px; margin-bottom: 6px;">Top Contributing Districts for {meta['name']}:</div>
                {rows_html}
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">
                Lead contributor: <strong>{top_h_dist['district']}</strong> accounts for {round((top_h_dist['count']/max(1, head_total))*100, 1)}% of all {meta['name'].lower()} across Karnataka.
            </div>
            """
            title = f"{meta['icon']} Karnataka Statewide: {meta['name']} ({year_str})"
            summary_text = f"Karnataka recorded {format_num(head_total)} {meta['name']} cases in {year_str}."

        elif category:
            cat_label = CATEGORY_NAMES.get(category, category.title())
            cat_total = state_categories.get(category, 0)
            pct_of_state = round((cat_total / max(1, state_total)) * 100, 1)

            cat_by_dist = []
            for d in self.all_districts:
                r = self.engine.get_record(d, year=year)
                cat_by_dist.append({'district': d, 'count': r['categories'].get(category, 0)})
            cat_by_dist.sort(key=lambda x: x['count'], reverse=True)
            top_c_dist = cat_by_dist[0]

            rows_html = "".join([
                f"<div style='display:flex; justify-content:space-between; padding:5px 8px; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
                f"<span>#{i+1} <strong>{item['district']}</strong></span>"
                f"<span style='color:#fff;'><strong>{format_num(item['count'])}</strong> cases ({round((item['count']/max(1, cat_total))*100, 1)}%)</span>"
                f"</div>"
                for i, item in enumerate(cat_by_dist[:5])
            ])

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                🛡️ Total recorded <strong>{cat_label}</strong> across all of Karnataka ({year_str}) stands at <strong style="color: #fff; font-size: 15px;">{format_num(cat_total)}</strong> cases ({pct_of_state}% of all {format_num(state_total)} IPC crimes).
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
                <div style="font-weight: 700; color: #ec4899; font-size: 12px; margin-bottom: 6px;">Top Contributing Districts for {cat_label}:</div>
                {rows_html}
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">
                Lead contributor: <strong>{top_c_dist['district']}</strong> accounts for {round((top_c_dist['count']/max(1, cat_total))*100, 1)}% of all {cat_label.lower()} in Karnataka.
            </div>
            """
            title = f"🛡️ Karnataka Statewide: {cat_label} ({year_str})"
            summary_text = f"Karnataka recorded {format_num(cat_total)} {cat_label} cases in {year_str}."

        else:
            cat_pills = "".join([
                f"<div style='background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:8px;'>"
                f"<div style='font-size:11px; color:var(--text-muted);'>{label}</div>"
                f"<div style='font-size:14px; font-weight:700; color:{CATEGORY_COLORS.get(cat, '#fff')};'>{format_num(cnt)}</div>"
                f"<div style='font-size:10px; color:var(--text-faint);'>{round((cnt/max(1, state_total))*100, 1)}% of state</div>"
                f"</div>"
                for cat, label in CATEGORY_NAMES.items()
                for cnt in [state_categories.get(cat, 0)]
            ])

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 10px;">
                🏛️ Total authentic IPC crimes recorded across all <strong>38 districts of Karnataka</strong> ({year_str}) stands at <strong style="color: #fff; font-size: 16px;">{format_num(state_total)}</strong> cases.<br>
                • <strong>{top_contributor['district']}</strong> is the largest single contributor, accounting for <strong>{format_num(top_contributor['total'])}</strong> cases ({round((top_contributor['total']/state_total)*100, 1)}% of Karnataka total).<br>
                • Average crime volume per district: <strong>{format_num(round(state_total/38))}</strong> cases.
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 10px 0;">
                {cat_pills}
            </div>
            """
            title = f"🏛️ Karnataka Statewide Crime Aggregate ({year_str})"
            summary_text = f"Karnataka recorded {format_num(state_total)} total crimes in {year_str}."

        suggestions = [
            "Which district has highest crime?",
            "Safest district in Karnataka",
            "Statewide murder count",
            "Crimes against women across Karnataka"
        ]

        return {
            'status': 'ok',
            'intent': 'statewide_aggregate',
            'year': year,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': suggestions
        }

    def _handle_district_analysis(self, district, year, crime_head, category):
        """Analyzes a specific named district, contextualized against the ENTIRE state of Karnataka."""
        r = self.engine.get_record(district, year=year)
        sum_data = self.engine.get_district_summary(district, year=year)
        year_str = "2016–2022" if year in ['all', 'combined'] else year

        all_district_totals = []
        state_total = 0
        for d in self.all_districts:
            rec = self.engine.get_record(d, year=year)
            tot = rec['total_crimes']
            state_total += tot
            all_district_totals.append((d, tot))

        all_district_totals.sort(key=lambda x: x[1], reverse=True)
        dist_rank = next((i + 1 for i, item in enumerate(all_district_totals) if item[0] == district), 1)
        state_share = round((r['total_crimes'] / max(1, state_total)) * 100, 1)
        state_avg = round(state_total / 38)

        if crime_head:
            meta = CRIME_HEAD_META.get(crime_head, {'name': crime_head.replace('_', ' ').title(), 'icon': '📌'})
            head_cnt = r['crimes'].get(crime_head, 0)
            head_pct = round((head_cnt / max(1, r['total_crimes'])) * 100, 1)

            head_rankings = []
            head_state_total = 0
            for d in self.all_districts:
                rec = self.engine.get_record(d, year=year)
                val = rec['crimes'].get(crime_head, 0)
                head_rankings.append((d, val))
                head_state_total += val
            head_rankings.sort(key=lambda x: x[1], reverse=True)
            head_rank = next((i + 1 for i, item in enumerate(head_rankings) if item[0] == district), 1)

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                {meta['icon']} In <strong>{district}</strong> ({year_str}), recorded <strong>{meta['name']}</strong> stands at <strong style="color: #fff; font-size: 15px;">{format_num(head_cnt)}</strong> cases.<br>
                • Represents <strong>{head_pct}%</strong> of all crimes in this district.<br>
                • Ranks <strong style="color: #38bdf8;">#{head_rank} out of 38</strong> districts in Karnataka for this offense ({round((head_cnt/max(1, head_state_total))*100, 1)}% of state total {format_num(head_state_total)}).
            </div>
            <div style="margin-top: 8px;">
                <button class="kcavp-chat-switch-btn btn-primary" data-district="{district}" style="padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer;">
                    View {district} in Dashboard →
                </button>
            </div>
            """
            title = f"{meta['icon']} {district}: {meta['name']} Analysis ({year_str})"
            summary_text = f"In {year_str}, {district} recorded {format_num(head_cnt)} {meta['name']} cases (Rank #{head_rank} in Karnataka)."
        else:
            top_off = sum_data['top_offense']
            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                📍 <strong>{district} Comprehensive Profile ({year_str}):</strong><br>
                • Total Recorded IPC Crimes: <strong style="color: #fff; font-size: 15px;">{format_num(r['total_crimes'])}</strong><br>
                • Karnataka Statewide Rank: <strong style="color: #38bdf8;">#{dist_rank} of 38 districts</strong> ({state_share}% of Karnataka's total {format_num(state_total)} crimes).<br>
                • Benchmark vs State Average ({format_num(state_avg)}): <strong style="color: {'#f43f5e' if r['total_crimes'] > state_avg else '#10b981'};">{'▲ +' if r['total_crimes'] > state_avg else '▼ '}{round(((r['total_crimes'] - state_avg)/state_avg)*100, 1)}%</strong>.<br>
                • Primary Threat Focus: <strong>{top_off['name']}</strong> ({format_num(top_off['count'])} cases, {top_off['percentage']}% share).
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin: 8px 0; font-size: 12px;">
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Violent:</span><br>
                    <strong style="color: #f43f5e;">{format_num(r['categories']['violent'])}</strong> ({sum_data['category_percentages']['violent']}%)
                </div>
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Property/Theft:</span><br>
                    <strong style="color: #60a5fa;">{format_num(r['categories']['property_economic'])}</strong> ({sum_data['category_percentages']['property_economic']}%)
                </div>
                <div style="background: rgba(255,255,255,0.03); padding: 6px 8px; border-radius: 6px;">
                    <span style="color: var(--text-muted); font-size: 11px;">Women/Children:</span><br>
                    <strong style="color: #ec4899;">{format_num(r['categories']['women_children'])}</strong> ({sum_data['category_percentages']['women_children']}%)
                </div>
            </div>
            <div style="margin-top: 8px;">
                <button class="kcavp-chat-switch-btn btn-primary" data-district="{district}" style="padding: 5px 12px; font-size: 12px; border-radius: 6px; cursor: pointer;">
                    View {district} in Dashboard →
                </button>
            </div>
            """
            title = f"📍 District Analysis: {district} ({year_str})"
            summary_text = f"{district} recorded {format_num(r['total_crimes'])} crimes (Rank #{dist_rank} in Karnataka)."

        suggestions = [
            f"Violent crimes in {district}",
            f"Thefts in {district}",
            f"Compare {district} and Bengaluru City",
            "Which district has highest crime?"
        ]

        return {
            'status': 'ok',
            'intent': 'district_analysis',
            'district': district,
            'year': year,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'highlight_district': district,
            'suggestions': suggestions
        }

    def _handle_trend(self, district, crime_head, category):
        """Analyzes historical 2016-2022 trajectory either statewide or for a district."""
        if not district:
            timeline = []
            for y in self.years:
                tot = sum(self.engine.records_by_district_year.get((d.lower(), y), {}).get('total_crimes', 0) for d in self.all_districts)
                timeline.append({'year': y, 'total': tot})

            first = timeline[0]['total']
            last = timeline[-1]['total']
            min_yr = min(timeline, key=lambda x: x['total'])
            net_chg = round(((last - first) / first) * 100, 1)

            rows_html = "".join([
                f"<div style='display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.05); font-size:12px;'>"
                f"<span>Year {t['year']}</span>"
                f"<strong style='color:#fff;'>{format_num(t['total'])} cases</strong>"
                f"</div>"
                for t in timeline
            ])

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                📈 <strong>Karnataka Statewide 7-Year Trajectory (2016 → 2022):</strong><br>
                • <strong>2016 Baseline</strong>: {format_num(first)} cases<br>
                • <strong>Lowest Level</strong>: {min_yr['year']} ({format_num(min_yr['total'])} cases during COVID-19 mobility curbs)<br>
                • <strong>2022 Latest</strong>: {format_num(last)} cases<br>
                Net 7-year statewide shift: <strong style="color: {'#f43f5e' if net_chg > 0 else '#10b981'};">{'+' if net_chg > 0 else ''}{net_chg}%</strong>.
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px; margin: 8px 0;">
                {rows_html}
            </div>
            """
            title = "📈 Karnataka 7-Year Statewide Crime Trajectory (2016–2022)"
            summary_text = f"Karnataka 7-year crime trajectory: from {format_num(first)} (2016) to {format_num(last)} (2022)."
        else:
            trend_data = self.engine.get_district_multi_year_trend(district)
            series = trend_data['series']
            first = series[0]['total']
            last = series[-1]['total']
            net_chg = round(((last - first) / max(1, first)) * 100, 1) if first > 0 else 0

            answer_html = f"""
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
                📈 <strong>7-Year Crime Trajectory in {district} (2016–2022):</strong><br>
                • <strong>2016 Baseline</strong>: {format_num(first)} cases<br>
                • <strong>2020 Lockdown</strong>: {format_num(next((s['total'] for s in series if s['year']=='2020'), 0))} cases<br>
                • <strong>2022 Latest</strong>: {format_num(last)} cases<br>
                Net 7-year shift in {district}: <strong style="color: {'#f43f5e' if net_chg > 0 else '#10b981'};">{'+' if net_chg > 0 else ''}{net_chg}%</strong>.
            </div>
            """
            title = f"📈 7-Year Trajectory: {district} (2016–2022)"
            summary_text = f"7-Year Trajectory analysis for {district}."

        suggestions = [
            "Which district had highest crime growth?",
            "Statewide total crimes in 2022",
            "Top 5 districts overall"
        ]

        return {
            'status': 'ok',
            'intent': 'trend_analysis',
            'district': district,
            'title': title,
            'summary_text': summary_text,
            'answer_html': answer_html,
            'suggestions': suggestions
        }

    def _handle_pinned_query(self, pinned_district):
        """Handles inquiries about the user's pinned watch-deck district."""
        sum_data = self.engine.get_district_summary(pinned_district, year='all')
        trend_data = self.engine.get_district_multi_year_trend(pinned_district)
        series = trend_data.get('series', [])

        first = series[0]['total'] if series else 0
        last = series[-1]['total'] if series else 0
        net_chg = round(((last - first) / max(1, first)) * 100, 1) if first > 0 else 0

        all_dist_totals = [(d, self.engine.get_record(d, year='all')['total_crimes']) for d in self.all_districts]
        all_dist_totals.sort(key=lambda x: x[1], reverse=True)
        rank = next((i + 1 for i, item in enumerate(all_dist_totals) if item[0] == pinned_district), 1)

        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            ⭐ <strong>Continuous Surveillance Deck: {pinned_district}</strong><br>
            Your pinned district is actively tracked with autonomous telemetry.<br>
            • Total Recorded IPC crimes (2016–2022): <strong style="color: #fff;">{format_num(sum_data['total_crimes'])}</strong><br>
            • Karnataka Rank: <strong style="color: #fbbf24;">#{rank} of 38 districts</strong><br>
            • Primary Threat: <strong>{sum_data['top_offense']['name']}</strong> ({format_num(sum_data['top_offense']['count'])} cases)<br>
            • 7-Year Net Trajectory: <strong style="color: {'#f43f5e' if net_chg > 0 else '#10b981'};">{'+' if net_chg > 0 else ''}{net_chg}%</strong> ({format_num(first)} in 2016 → {format_num(last)} in 2022).
        </div>
        """

        return {
            'status': 'ok',
            'intent': 'pinned_surveillance',
            'district': pinned_district,
            'title': f"⭐ Continuous Surveillance Deck: {pinned_district}",
            'summary_text': f"Your pinned district {pinned_district} has {format_num(sum_data['total_crimes'])} cases.",
            'answer_html': answer_html,
            'suggestions': [
                f"Violent crimes in {pinned_district}",
                f"Compare {pinned_district} and Bengaluru City",
                "Which district has highest crime?",
                "Safest district in Karnataka"
            ]
        }

    def _handle_conversational_fallback(self, query, current_district, year):
        """Conversational fallback explaining analytical capabilities with real dataset numbers."""
        state_total = sum(self.engine.aggregated_by_district[d.lower()]['total_crimes'] for d in self.all_districts)
        answer_html = f"""
        <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-main); margin-bottom: 8px;">
            🤖 <strong>Karnataka Crime Analytics Intelligence</strong><br>
            I analyze <strong>{format_num(state_total)} total authentic IPC records</strong> covering <strong>all 38 districts</strong> across Karnataka (2016–2022).<br>
            You can ask me questions about specific years, specific districts, comparisons, or statewide rankings!
        </div>
        <div style="margin-top: 8px; font-size: 12px; color: var(--text-muted);">
            💡 <strong>Example Questions You Can Ask:</strong>
            <ul style="margin: 6px 0 0 16px; padding: 0; line-height: 1.6;">
                <li><em>"How many crimes in 2022?"</em> (Statewide summary for 2022)</li>
                <li><em>"Which district has most murders in 2022?"</em> (Offense leader by year)</li>
                <li><em>"Safest district in Karnataka"</em> (Lowest crime districts)</li>
                <li><em>"Crime in Tumakuru in 2021"</em> (District analysis for a specific year)</li>
                <li><em>"Compare 2016 and 2022"</em> (Multi-year comparison)</li>
                <li><em>"Compare Bengaluru City and Mysuru City"</em> (District vs District)</li>
            </ul>
        </div>
        """

        return {
            'status': 'ok',
            'intent': 'conversational_help',
            'title': "🤖 KCAVP Crime Intelligence Assistant",
            'summary_text': "Ask any question about Karnataka's 38 districts, years 2016-2022, or 34 crime heads.",
            'answer_html': answer_html,
            'suggestions': self._get_default_suggestions()
        }

    def _get_default_suggestions(self):
        return [
            "How many crimes in 2022?",
            "Which district has highest crime?",
            "Safest district in Karnataka",
            "Which district has most murders in 2022?",
            "Compare Bengaluru City and Mysuru City"
        ]
