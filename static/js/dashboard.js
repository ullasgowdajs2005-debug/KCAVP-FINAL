/**
 * KCAVP — Karnataka Single-District Crime Analytics & Visualization Platform
 * Client Application Controller & Chart Engine
 * Comprehensive 7-Year Multi-Year Support (2016 through 2022)
 * With Continuous Preferred District Surveillance Tracking
 */

(function () {
    const initialSummary = window.KCAVP_INITIAL_SUMMARY || {};
    const initialOffenses = window.KCAVP_INITIAL_OFFENSES || [];
    const initialCritical = window.KCAVP_INITIAL_CRITICAL || [];
    const initialCategories = window.KCAVP_INITIAL_CATEGORIES || {};
    const initialTable = window.KCAVP_INITIAL_TABLE || {};
    const initialTrends = window.KCAVP_INITIAL_TRENDS || {};

    // Retrieve saved pinned district or fallback to Bengaluru City (ISOLATED from main view)
    const savedPinnedDistrict = localStorage.getItem('kcavp_pinned_district') || 'Bengaluru City';

    // Check if URL specifies district, otherwise use default district (DO NOT fallback to pinned district)
    const urlParams = new URLSearchParams(window.location.search);
    const districtFromUrl = urlParams.get('district');
    const initialActiveDistrict = districtFromUrl || window.KCAVP_DEFAULT_DISTRICT || 'Bengaluru City';

    const state = {
        selectedDistrict: initialActiveDistrict,
        pinnedDistrict: savedPinnedDistrict,
        selectedYear: window.KCAVP_SELECTED_YEAR || 'all',
        selectedCategory: 'all',
        tableSearch: '',
        tableSortBy: 'count',
        tableSortOrder: 'desc',
        theme: localStorage.getItem('kcavp_theme') || 'dark'
    };

    let offensesBarChart = null;
    let donutChart = null;
    let trendLineChart = null;
    let criticalChart = null;
    let radarChart = null;

    // Dedicated Distinct Visualizations for Pinned District Cockpit
    let pinnedGaugeChart = null;
    let pinnedMomentumChart = null;

    // Deep-Dive Modal Chart Instances
    let kpiModalChart1 = null;
    let kpiModalChart2 = null;
    let currentModalKpiType = null;

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = document.getElementById('themeToggleIcon');
        if (icon) icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    applyTheme(state.theme);

    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', function () {
            state.theme = state.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('kcavp_theme', state.theme);
            applyTheme(state.theme);
            if (offensesBarChart) offensesBarChart.update();
            if (donutChart) donutChart.update();
            if (trendLineChart) trendLineChart.update();
            if (criticalChart) criticalChart.update();
            if (radarChart) radarChart.update();
            if (pinnedGaugeChart) pinnedGaugeChart.update();
            if (pinnedMomentumChart) pinnedMomentumChart.update();
            if (kpiModalChart1) kpiModalChart1.update();
            if (kpiModalChart2) kpiModalChart2.update();
        });
    }

    function formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return Number(num).toLocaleString('en-IN');
    }

    // =========================================================================
    // PINNED DISTRICT SURVEILLANCE COCKPIT (100% ISOLATED MODULE)
    // =========================================================================
    function setPinnedDistrict(districtName) {
        if (!districtName) return;
        state.pinnedDistrict = districtName;
        localStorage.setItem('kcavp_pinned_district', districtName);

        // Update Navbar quick shortcut text
        const navPrefLabel = document.getElementById('preferredDistrictLabel');
        if (navPrefLabel) navPrefLabel.textContent = `Pinned: ${districtName}`;

        // Update Cockpit title
        const cardTitle = document.getElementById('pinnedDeckTitleDistrict');
        if (cardTitle) cardTitle.textContent = districtName;

        // Sync dropdown selector in pinned deck
        const pinnedSelect = document.getElementById('pinnedDistrictSelect');
        if (pinnedSelect) pinnedSelect.value = districtName;

        // Update Hero star button icon/label
        updateTrackButtonState();

        // Refresh ONLY the Pinned Cockpit (Zero effect on main explorer & AI chatbot)
        updatePinnedDeck(districtName);
    }

    function updateTrackButtonState() {
        const btn = document.getElementById('trackDistrictBtn');
        const star = document.getElementById('trackStarIcon');
        const text = document.getElementById('trackBtnText');
        if (!btn) return;

        const isPinned = (state.selectedDistrict === state.pinnedDistrict);
        if (isPinned) {
            btn.classList.add('tracked');
            if (star) star.textContent = '★';
            if (text) text.textContent = 'Active in Watch Deck';
            btn.title = `${state.selectedDistrict} is actively monitored in your Pinned Surveillance Deck`;
        } else {
            btn.classList.remove('tracked');
            if (star) star.textContent = '⭐';
            if (text) text.textContent = 'Pin to Watch Deck';
            btn.title = `Click to pin ${state.selectedDistrict} to your continuous surveillance watch deck`;
        }
    }

    // Distinct Visualization 1: Safety Threat & Risk Gauge Meter (Semi-doughnut Speedometer)
    function initPinnedGaugeChart(score, tierColor) {
        const canvas = document.getElementById('pinnedThreatGaugeCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (pinnedGaugeChart) {
            try { pinnedGaugeChart.destroy(); } catch (e) {}
            pinnedGaugeChart = null;
        }

        const clampedScore = Math.max(0, Math.min(100, Math.round(score || 0)));
        const remaining = 100 - clampedScore;
        const activeColor = tierColor || '#fbbf24';

        pinnedGaugeChart = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Risk Score', 'Remaining Capacity'],
                datasets: [
                    {
                        // Outer primary gauge arc
                        data: [clampedScore, remaining],
                        backgroundColor: [activeColor, 'rgba(255, 255, 255, 0.05)'],
                        borderWidth: 0,
                        circumference: 180,
                        rotation: 270,
                        cutout: '76%',
                        borderRadius: [6, 0]
                    },
                    {
                        // Inner reference track (Low 0-35 / Moderate 35-65 / Critical 65-100 zones)
                        data: [35, 30, 35],
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.35)',
                            'rgba(245, 158, 11, 0.35)',
                            'rgba(244, 63, 94, 0.35)'
                        ],
                        borderWidth: 1,
                        borderColor: 'rgba(15, 23, 42, 0.7)',
                        circumference: 180,
                        rotation: 270,
                        cutout: '88%'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 900,
                    animateRotate: true
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: function (ctx) {
                                if (ctx.datasetIndex === 0) {
                                    return ctx.dataIndex === 0 ? ` Risk Threat Score: ${clampedScore}/100` : '';
                                }
                                const zoneNames = [' Safe Tier (0–35 Score)', ' Guarded Vigilance Tier (35–65 Score)', ' Critical Alert Tier (65–100 Score)'];
                                return zoneNames[ctx.dataIndex] || '';
                            }
                        }
                    }
                }
            }
        });
    }

    // Distinct Visualization 2: Diverging Annual Momentum & Volatility Bar Chart
    function initPinnedMomentumChart(series) {
        const canvas = document.getElementById('pinnedMomentumCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (pinnedMomentumChart) {
            try { pinnedMomentumChart.destroy(); } catch (e) {}
            pinnedMomentumChart = null;
        }

        series = series || [];
        const labels = [];
        const yoyValues = [];
        const bgColors = [];
        const borderColors = [];
        const caseDeltas = [];

        for (let i = 1; i < series.length; i++) {
            const cur = series[i];
            const prev = series[i - 1];
            labels.push(`'${String(prev.year).slice(-2)}→'${String(cur.year).slice(-2)}`);
            const delta = (cur.total || 0) - (prev.total || 0);
            caseDeltas.push(delta);
            let pct = 0;
            if (prev.total > 0) {
                pct = Number((((cur.total - prev.total) / prev.total) * 100).toFixed(1));
            }
            yoyValues.push(pct);
            if (pct >= 0) {
                bgColors.push('rgba(244, 63, 94, 0.85)');
                borderColors.push('#f43f5e');
            } else {
                bgColors.push('rgba(16, 185, 129, 0.85)');
                borderColors.push('#10b981');
            }
        }

        const footer = document.getElementById('pinnedMomentumSummaryText');
        if (footer && yoyValues.length > 0) {
            const latest = yoyValues[yoyValues.length - 1];
            const latestDelta = caseDeltas[caseDeltas.length - 1];
            const arrow = latest >= 0 ? '▲' : '▼';
            const status = latest < 0 ? 'decelerating (improving)' : 'surging (escalation)';
            footer.innerHTML = `
                Latest 2021→2022 Momentum: <strong style="color: ${latest < 0 ? '#10b981' : '#f43f5e'};">${arrow} ${latest > 0 ? '+' : ''}${latest}%</strong>
                (${formatNumber(Math.abs(latestDelta))} ${latestDelta >= 0 ? 'more' : 'fewer'} cases), indicating crime velocity is <strong>${status}</strong>.
            `;
        }

        pinnedMomentumChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'YoY % Shift',
                    data: yoyValues,
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: 1.5,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 850
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                const val = ctx.parsed.y;
                                const delta = caseDeltas[ctx.dataIndex];
                                const sign = val > 0 ? '+' : '';
                                const deltaSign = delta > 0 ? '+' : '';
                                return ` YoY Shift: ${sign}${val}% (${deltaSign}${formatNumber(delta)} cases)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11, weight: '600' }
                        }
                    },
                    y: {
                        grid: {
                            color: function (ctx) {
                                return ctx.tick.value === 0 ? 'rgba(255, 255, 255, 0.4)' : 'rgba(255, 255, 255, 0.05)';
                            },
                            lineWidth: function (ctx) {
                                return ctx.tick.value === 0 ? 2 : 1;
                            }
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 10 },
                            callback: function (val) {
                                return (val > 0 ? '+' : '') + val + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Distinct Visualization 3: Surveillance Category Proportional Heatstrip
    function updatePinnedHeatstrip(cats, total) {
        const bar = document.getElementById('pinnedHeatstripBar');
        const legend = document.getElementById('pinnedHeatstripLegend');
        if (!bar || !legend) return;

        const catMeta = [
            { key: 'property_economic', label: 'Property & Theft', color: '#3b82f6' },
            { key: 'public_safety', label: 'Traffic & Safety', color: '#f59e0b' },
            { key: 'women_children', label: 'Women & Child', color: '#ec4899' },
            { key: 'violent', label: 'Violent Crimes', color: '#f43f5e' },
            { key: 'public_order', label: 'Public Order', color: '#8b5cf6' }
        ];

        const tot = total || 1;
        let barHtml = '';
        let legHtml = '';

        catMeta.forEach(c => {
            const count = (cats && cats[c.key]) ? cats[c.key] : 0;
            const pct = ((count / tot) * 100).toFixed(1);
            barHtml += `<div class="pinned-heatstrip-seg" style="width: ${pct}%; background: ${c.color};" title="${c.label}: ${formatNumber(count)} cases (${pct}%)"></div>`;
            legHtml += `
                <div class="pinned-hl-item">
                    <span class="pinned-hl-dot" style="background: ${c.color};"></span>
                    <span>${c.label}: <strong style="color: #f8fafc;">${pct}%</strong></span>
                </div>
            `;
        });

        bar.innerHTML = barHtml;
        legend.innerHTML = legHtml;
    }

    // Updates all elements inside the Pinned District Surveillance Cockpit (Zero side-effects)
    function updatePinnedDeck(districtName) {
        if (!districtName) return;
        const distEncoded = encodeURIComponent(districtName);

        fetch(`/api/summary/?district=${distEncoded}&year=all`)
            .then(r => r.json())
            .then(summary => {
                const elTotal = document.getElementById('pinnedMetricTotal');
                const elThreat = document.getElementById('pinnedMetricTopThreat');
                const elThreatCount = document.getElementById('pinnedMetricThreatCount');

                if (elTotal) elTotal.textContent = `${formatNumber(summary.total_crimes)} cases`;
                if (elThreat) elThreat.textContent = summary.top_offense?.name || 'N/A';
                if (elThreatCount) {
                    elThreatCount.textContent = `${formatNumber(summary.top_offense?.count || 0)} cases (${summary.top_offense?.percentage || 0}%)`;
                }

                // Update Category Heatstrip
                updatePinnedHeatstrip(summary.categories || {}, summary.total_crimes || 1);

                // Fetch multi-year trends for diverging momentum and compound shift
                fetch(`/api/trends/?district=${distEncoded}`)
                    .then(r2 => r2.json())
                    .then(trends => {
                        const series = trends.series || [];
                        const first = series[0] || {};
                        const last = series[series.length - 1] || {};
                        const prev = series[series.length - 2] || {};

                        // Multi-year Net Shift
                        const elTrend = document.getElementById('pinnedMetricTrend');
                        const elTrendSub = document.getElementById('pinnedMetricTrendSub');
                        let netShift = 0;
                        if (first.total > 0) {
                            netShift = (((last.total - first.total) / first.total) * 100).toFixed(1);
                        }
                        if (elTrend) {
                            const sign = netShift > 0 ? '+' : '';
                            const arrow = netShift > 0 ? '▲' : (netShift < 0 ? '▼' : '●');
                            elTrend.textContent = `${arrow} ${sign}${netShift}%`;
                            elTrend.style.color = netShift < 0 ? '#10b981' : (netShift > 0 ? '#f43f5e' : '#cbd5e1');
                        }
                        if (elTrendSub) {
                            elTrendSub.textContent = `2016 (${formatNumber(first.total)}) → 2022 (${formatNumber(last.total)}) Net Shift`;
                        }

                        // Calculate YoY for latest year
                        let latestYoY = 0;
                        if (prev.total > 0) {
                            latestYoY = (((last.total - prev.total) / prev.total) * 100);
                        }

                        // Calculate Safety Threat & Vulnerability Index (0-100 score)
                        const violentPct = summary.category_percentages?.violent || 0;
                        const totalCrimes = summary.total_crimes || 0;

                        const vScore = Math.min(40, violentPct * 2.2);
                        const volScore = Math.min(30, (totalCrimes / 200000) * 30);
                        let trScore = 15;
                        if (latestYoY > 15) trScore = 30;
                        else if (latestYoY > 5) trScore = 24;
                        else if (latestYoY > -5) trScore = 18;
                        else trScore = 8;

                        const threatScore = Math.min(99, Math.max(12, Math.round(vScore + volScore + trScore)));

                        let tierName = 'Guarded Vigilance';
                        let tierColor = '#f59e0b';
                        let advisorySub = 'Standard surveillance threshold';

                        if (threatScore <= 35) {
                            tierName = 'Low Threat Tier';
                            tierColor = '#10b981';
                            advisorySub = 'Minimal risk index recorded';
                        } else if (threatScore > 65) {
                            tierName = 'Critical Alert Tier';
                            tierColor = '#f43f5e';
                            advisorySub = 'Elevated threat density identified';
                        }

                        // Update Score Display
                        const elScore = document.getElementById('pinnedGaugeScore');
                        const elStatus = document.getElementById('pinnedGaugeStatusTag');
                        const elBadge = document.getElementById('pinnedGaugeTierBadge');
                        const elAdvisory = document.getElementById('pinnedMetricAdvisory');
                        const elAdvisorySub = document.getElementById('pinnedMetricAdvisorySub');

                        if (elScore) {
                            elScore.textContent = threatScore;
                            elScore.style.color = tierColor;
                            elScore.style.textShadow = `0 0 16px ${tierColor}66`;
                        }
                        if (elStatus) {
                            elStatus.textContent = tierName;
                            elStatus.style.background = `${tierColor}25`;
                            elStatus.style.color = tierColor;
                        }
                        if (elBadge) {
                            elBadge.textContent = tierName;
                            elBadge.style.background = `${tierColor}20`;
                            elBadge.style.color = tierColor;
                        }
                        if (elAdvisory) {
                            elAdvisory.textContent = tierName;
                            elAdvisory.style.color = tierColor;
                        }
                        if (elAdvisorySub) {
                            elAdvisorySub.textContent = advisorySub;
                        }

                        // Render Speedometer Gauge Chart
                        initPinnedGaugeChart(threatScore, tierColor);

                        // Render Diverging Momentum Bar Chart
                        initPinnedMomentumChart(series);
                    })
                    .catch(console.error);
            })
            .catch(console.error);
    }

    function renderKPIs(data) {
        if (!data) return;
        const elTotal = document.getElementById('kpiTotalCrimes');
        if (elTotal) elTotal.textContent = formatNumber(data.total_crimes || 0);

        const elDistrictBadge = document.getElementById('kpiDistrictBadge');
        if (elDistrictBadge) elDistrictBadge.textContent = data.district || state.selectedDistrict;

        const elYearBadge = document.getElementById('kpiYearLabel');
        if (elYearBadge) elYearBadge.textContent = data.year_display || 'Official Dataset';

        const elHeroBadge = document.getElementById('heroYearBadge');
        if (elHeroBadge) elHeroBadge.textContent = data.year_display || '2016–2022';

        const elYoYBadge = document.getElementById('kpiYoYBadge');
        if (elYoYBadge) {
            const growth = data.yoy_growth;
            if (growth !== null && growth !== undefined && data.prev_year && data.prev_year !== 'None') {
                elYoYBadge.style.display = 'inline-flex';
                const sign = growth > 0 ? '+' : '';
                const arrow = growth > 0 ? '▲' : (growth < 0 ? '▼' : '●');
                elYoYBadge.textContent = `${arrow} ${sign}${growth}% vs ${data.prev_year}`;
                if (growth < 0) {
                    elYoYBadge.style.background = 'rgba(16, 185, 129, 0.15)';
                    elYoYBadge.style.color = '#10b981';
                } else if (growth > 0) {
                    elYoYBadge.style.background = 'rgba(244, 63, 94, 0.15)';
                    elYoYBadge.style.color = '#f43f5e';
                } else {
                    elYoYBadge.style.background = 'rgba(148, 163, 184, 0.15)';
                    elYoYBadge.style.color = '#94a3b8';
                }
            } else {
                elYoYBadge.style.display = 'none';
            }
        }

        const elProperty = document.getElementById('kpiProperty');
        const elPropertyPct = document.getElementById('kpiPropertyPct');
        if (elProperty) elProperty.textContent = formatNumber(data.categories?.property_economic || 0);
        if (elPropertyPct) elPropertyPct.textContent = `${data.category_percentages?.property_economic || 0}% of district total`;

        const elSafety = document.getElementById('kpiSafety');
        const elSafetyPct = document.getElementById('kpiSafetyPct');
        if (elSafety) elSafety.textContent = formatNumber(data.categories?.public_safety || 0);
        if (elSafetyPct) elSafetyPct.textContent = `${data.category_percentages?.public_safety || 0}% of district total`;

        const elWomen = document.getElementById('kpiWomen');
        const elWomenPct = document.getElementById('kpiWomenPct');
        if (elWomen) elWomen.textContent = formatNumber(data.categories?.women_children || 0);
        if (elWomenPct) elWomenPct.textContent = `${data.category_percentages?.women_children || 0}% of district total`;

        const elViolent = document.getElementById('kpiViolent');
        const elViolentPct = document.getElementById('kpiViolentPct');
        if (elViolent) elViolent.textContent = formatNumber(data.categories?.violent || 0);
        if (elViolentPct) elViolentPct.textContent = `${data.category_percentages?.violent || 0}% of district total`;

        const elTopName = document.getElementById('kpiTopOffenseName');
        const elTopCount = document.getElementById('kpiTopOffenseCount');
        if (elTopName) elTopName.textContent = data.top_offense?.name || 'N/A';
        if (elTopCount) {
            elTopCount.textContent = `${formatNumber(data.top_offense?.count || 0)} cases (${data.top_offense?.percentage || 0}%)`;
        }

        const spanBar = document.getElementById('barChartYearSpan');
        if (spanBar) spanBar.textContent = data.year_display || 'Selected Period';

        const spanDonut = document.getElementById('donutYearSpan');
        if (spanDonut) spanDonut.textContent = data.year_display || 'Selected Period';

        const spanRadar = document.getElementById('radarYearSpan');
        if (spanRadar) spanRadar.textContent = data.year_display || 'Selected Period';

        const spanTableYear = document.getElementById('tableYearName');
        if (spanTableYear) spanTableYear.textContent = data.year_display || 'Selected Period';
    }

    function initOffensesBarChart(offenses) {
        const canvas = document.getElementById('offensesBarCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (offensesBarChart) {
            try { offensesBarChart.destroy(); } catch (e) {}
            offensesBarChart = null;
        }
        const ctx = canvas.getContext('2d');
        offenses = offenses || [];

        offensesBarChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: offenses.map(o => o.name),
                datasets: [{
                    label: 'Recorded Cases',
                    data: offenses.map(o => o.count),
                    backgroundColor: offenses.map(o => o.color || '#3b82f6'),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.94)',
                        callbacks: {
                            label: function (ctx) {
                                const off = offenses[ctx.dataIndex];
                                return ` Cases: ${formatNumber(ctx.raw)} (${off?.percentage || 0}% of district total)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'JetBrains Mono', size: 10 },
                            callback: function (val) { return val >= 1000 ? (val / 1000) + 'k' : val; }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11, weight: 500 } }
                    }
                }
            }
        });
    }

    function updateOffensesBarChart(offenses) {
        offenses = offenses || [];
        if (!offensesBarChart || !offensesBarChart.ctx || !offensesBarChart.data || !offensesBarChart.data.datasets || !offensesBarChart.data.datasets[0]) {
            initOffensesBarChart(offenses);
            return;
        }
        offensesBarChart.data.labels = offenses.map(o => o.name);
        offensesBarChart.data.datasets[0].data = offenses.map(o => o.count);
        offensesBarChart.data.datasets[0].backgroundColor = offenses.map(o => o.color || '#3b82f6');
        offensesBarChart.update();
    }

    function initDonutChart(catData) {
        const canvas = document.getElementById('donutChartCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (donutChart) {
            try { donutChart.destroy(); } catch (e) {}
            donutChart = null;
        }
        const ctx = canvas.getContext('2d');
        catData = catData || {};
        const categories = catData.categories || [];

        donutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categories.map(c => c.label),
                datasets: [{
                    data: categories.map(c => c.count),
                    backgroundColor: categories.map(c => c.color),
                    borderWidth: 2,
                    borderColor: 'var(--bg-surface)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.94)',
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const val = context.raw || 0;
                                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${formatNumber(val)} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    function updateDonutChart(catData) {
        catData = catData || {};
        const categories = catData.categories || [];
        if (!donutChart || !donutChart.ctx || !donutChart.data || !donutChart.data.datasets || !donutChart.data.datasets[0]) {
            initDonutChart(catData);
            return;
        }
        donutChart.data.labels = categories.map(c => c.label);
        donutChart.data.datasets[0].data = categories.map(c => c.count);
        donutChart.data.datasets[0].backgroundColor = categories.map(c => c.color);
        donutChart.update();

        const legendContainer = document.getElementById('categoryLegendContainer');
        if (legendContainer && categories.length > 0) {
            legendContainer.innerHTML = categories.map(c => `
                <div class="cat-legend-item">
                    <span class="cat-dot" style="background: ${c.color};"></span>
                    <span class="cat-name">${c.label}</span>
                    <span class="cat-count">${c.percentage || 0}%</span>
                </div>
            `).join('');
        }
    }

    function initTrendLineChart(trendData) {
        const canvas = document.getElementById('trendLineCanvas');
        if (!canvas || !trendData || !trendData.years || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (trendLineChart) {
            try { trendLineChart.destroy(); } catch (e) {}
            trendLineChart = null;
        }
        const ctx = canvas.getContext('2d');

        const series = trendData.series || [];
        const years = trendData.years || ['2016', '2017', '2018', '2019', '2020', '2021', '2022'];

        trendLineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [
                    {
                        label: 'Total District Crimes',
                        data: series.map(s => s.total),
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.12)',
                        borderWidth: 3,
                        pointRadius: 5,
                        pointBackgroundColor: '#06b6d4',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 8,
                        tension: 0.25,
                        fill: true
                    },
                    {
                        label: 'Property & Thefts',
                        data: series.map(s => s.property_economic),
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#3b82f6',
                        borderDash: [4, 4],
                        tension: 0.2
                    },
                    {
                        label: 'Traffic & Accidents',
                        data: series.map(s => s.public_safety),
                        borderColor: '#f59e0b',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b',
                        tension: 0.2
                    },
                    {
                        label: 'Women & Child Safety',
                        data: series.map(s => s.women_children),
                        borderColor: '#ec4899',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#ec4899',
                        tension: 0.2
                    },
                    {
                        label: 'Violent Offenses',
                        data: series.map(s => s.violent),
                        borderColor: '#f43f5e',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#f43f5e',
                        tension: 0.2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 11, weight: 500 },
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.94)',
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.dataset.label}: ${formatNumber(ctx.raw)} cases`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#cbd5e1', font: { family: 'Inter', size: 11, weight: 600 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'JetBrains Mono', size: 10 },
                            callback: function (val) { return val >= 1000 ? (val / 1000) + 'k' : val; }
                        }
                    }
                }
            }
        });
    }

    function updateTrendLineChart(trendData) {
        trendData = trendData || {};
        if (!trendLineChart || !trendData.series || !trendLineChart.ctx || !trendLineChart.data || !trendLineChart.data.datasets || trendLineChart.data.datasets.length < 5) {
            initTrendLineChart(trendData);
            return;
        }
        const series = trendData.series || [];
        trendLineChart.data.labels = trendData.years || ['2016', '2017', '2018', '2019', '2020', '2021', '2022'];
        trendLineChart.data.datasets[0].data = series.map(s => s.total);
        trendLineChart.data.datasets[1].data = series.map(s => s.property_economic);
        trendLineChart.data.datasets[2].data = series.map(s => s.public_safety);
        trendLineChart.data.datasets[3].data = series.map(s => s.women_children);
        trendLineChart.data.datasets[4].data = series.map(s => s.violent);
        trendLineChart.update();
    }

    function renderAnnualShift(trendData) {
        const container = document.getElementById('annualShiftContainer');
        if (!container) return;

        const series = trendData.series || [];
        if (series.length === 0) return;

        const first = series[0] || { year: '2016', total: 0 };
        const last = series[series.length - 1] || { year: '2022', total: 0 };

        const s2019 = series.find(s => s.year === '2019') || { total: 0 };
        const s2020 = series.find(s => s.year === '2020') || { total: 0 };

        const netChg = first.total > 0 ? (((last.total - first.total) / first.total) * 100).toFixed(1) : 0;
        const netSign = netChg > 0 ? '+' : '';

        const pandemicChg = s2019.total > 0 ? (((s2020.total - s2019.total) / s2019.total) * 100).toFixed(1) : 0;
        const panSign = pandemicChg > 0 ? '+' : '';

        container.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--border-color);">
                <div>
                    <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">2016 Baseline Recording</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">${formatNumber(first.total)} cases</div>
                </div>
                <span class="trend-pill trend-neutral">Base Year</span>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--border-color);">
                <div>
                    <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">2020 Pandemic Lockdown Year</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">${formatNumber(s2020.total)} cases</div>
                </div>
                <span class="trend-pill" style="background: ${pandemicChg < 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)'}; color: ${pandemicChg < 0 ? '#10b981' : '#f43f5e'};">
                    ${panSign}${pandemicChg}% vs 2019
                </span>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.03); border-radius: 8px; border: 1px solid var(--border-color);">
                <div>
                    <div style="font-size: 11px; color: var(--text-muted); font-weight: 600;">2022 Latest NCRB Report</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">${formatNumber(last.total)} cases</div>
                </div>
                <span class="trend-pill" style="background: ${netChg < 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)'}; color: ${netChg < 0 ? '#10b981' : '#f43f5e'};">
                    ${netSign}${netChg}% vs 2016
                </span>
            </div>
        `;
    }

    function initCriticalChart(critical) {
        const canvas = document.getElementById('criticalOffensesCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (criticalChart) {
            try { criticalChart.destroy(); } catch (e) {}
            criticalChart = null;
        }
        const ctx = canvas.getContext('2d');
        critical = critical || [];

        criticalChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: critical.map(c => c.name),
                datasets: [{
                    label: 'Recorded Cases',
                    data: critical.map(c => c.count),
                    backgroundColor: 'rgba(244, 63, 94, 0.85)',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.94)',
                        callbacks: { label: function (ctx) { return ` Cases: ${formatNumber(ctx.raw)}`; } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11, weight: 500 } }
                    }
                }
            }
        });
    }

    function updateCriticalChart(critical) {
        critical = critical || [];
        if (!criticalChart || !criticalChart.ctx || !criticalChart.data || !criticalChart.data.datasets || !criticalChart.data.datasets[0]) {
            initCriticalChart(critical);
            return;
        }
        criticalChart.data.labels = critical.map(c => c.name);
        criticalChart.data.datasets[0].data = critical.map(c => c.count);
        criticalChart.update();
    }

    function initRadarChart(summaryData) {
        const canvas = document.getElementById('radarChartCanvas');
        if (!canvas || typeof Chart === 'undefined') return;
        const existing = Chart.getChart(canvas);
        if (existing) {
            try { existing.destroy(); } catch (e) {}
        }
        if (radarChart) {
            try { radarChart.destroy(); } catch (e) {}
            radarChart = null;
        }
        const ctx = canvas.getContext('2d');
        summaryData = summaryData || {};

        const catLabels = ['Property', 'Traffic Safety', 'Women & Children', 'Violent', 'Public Order', 'Other IPC'];
        const catKeys = ['property_economic', 'public_safety', 'women_children', 'violent', 'public_order', 'other'];
        const dataVals = catKeys.map(k => (summaryData.category_percentages && summaryData.category_percentages[k]) || 0);

        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: catLabels,
                datasets: [{
                    label: `${summaryData.district || state.selectedDistrict} Profile`,
                    data: dataVals,
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    borderColor: '#6366f1',
                    pointBackgroundColor: '#818cf8',
                    pointBorderColor: '#ffffff',
                    pointRadius: 4,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.94)',
                        callbacks: { label: function (ctx) { return ` ${ctx.dataset.label}: ${ctx.raw}% of district total`; } }
                    }
                },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                        grid: { color: 'rgba(255, 255, 255, 0.06)' },
                        pointLabels: { color: '#cbd5e1', font: { family: 'Inter', size: 11, weight: 500 } },
                        ticks: { display: false, stepSize: 10 },
                        suggestedMin: 0,
                        suggestedMax: 40
                    }
                }
            }
        });
    }

    function updateRadarChart(summaryData) {
        summaryData = summaryData || {};
        if (!radarChart || !radarChart.ctx || !radarChart.data || !radarChart.data.datasets || !radarChart.data.datasets[0]) {
            initRadarChart(summaryData);
            return;
        }
        const catKeys = ['property_economic', 'public_safety', 'women_children', 'violent', 'public_order', 'other'];
        const dataVals = catKeys.map(k => (summaryData.category_percentages && summaryData.category_percentages[k]) || 0);
        radarChart.data.datasets[0].label = `${summaryData.district || state.selectedDistrict} Profile`;
        radarChart.data.datasets[0].data = dataVals;
        radarChart.update();
    }

    function renderTable(tableData) {
        const tbody = document.getElementById('dataTableBody');
        const info = document.getElementById('tablePaginationInfo');
        if (!tbody) return;

        const rows = tableData.rows || [];
        if (rows.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 30px; color: var(--text-muted);">No offenses matching search criteria</td></tr>`;
        } else {
            tbody.innerHTML = rows.map(r => `
                <tr>
                    <td style="font-weight: 600; color: var(--text-main);">
                        <span style="margin-right: 6px;">${r.icon || '📌'}</span> ${r.name}
                    </td>
                    <td>
                        <span style="color: ${r.color}; font-weight: 500;">${r.category_label}</span>
                    </td>
                    <td class="num-cell bold-cell">${formatNumber(r.count)}</td>
                    <td class="num-cell" style="font-family: var(--font-mono); color: var(--text-muted);">${r.percentage}%</td>
                    <td>
                        <span class="tile-tier-badge" style="
                            ${r.tier_badge === 'danger' ? 'background: rgba(244, 63, 94, 0.2); color: #f43f5e;' : ''}
                            ${r.tier_badge === 'warning' ? 'background: rgba(245, 158, 11, 0.2); color: #f59e0b;' : ''}
                            ${r.tier_badge === 'info' ? 'background: rgba(59, 130, 246, 0.2); color: #60a5fa;' : ''}
                        ">${r.tier}</span>
                    </td>
                </tr>
            `).join('');
        }

        if (info) {
            const yLabel = state.selectedYear === 'all' ? '2016–2022 Combined' : `Year ${state.selectedYear}`;
            info.textContent = `Showing all ${rows.length} of ${tableData.total_heads || 34} individual IPC crime heads in ${tableData.district || state.selectedDistrict} (${yLabel})`;
        }
    }

    function fetchTableData() {
        const catParam = state.selectedCategory !== 'all' ? `&category=${encodeURIComponent(state.selectedCategory)}` : '';
        const yearParam = `&year=${encodeURIComponent(state.selectedYear)}`;
        const url = `/api/table/?district=${encodeURIComponent(state.selectedDistrict)}${yearParam}${catParam}&search=${encodeURIComponent(state.tableSearch)}&sort_by=${state.tableSortBy}&order=${state.tableSortOrder}`;
        fetch(url).then(res => res.json()).then(data => renderTable(data)).catch(console.error);
    }

    function syncUIState() {
        const loading = document.getElementById('globalLoadingIndicator');
        if (loading) loading.style.display = 'inline';

        const distEncoded = encodeURIComponent(state.selectedDistrict);
        const yearEncoded = encodeURIComponent(state.selectedYear);
        const catParam = state.selectedCategory !== 'all' ? `&category=${encodeURIComponent(state.selectedCategory)}` : '';

        // Update URL query parameters
        if (window.history && window.history.pushState) {
            const params = new URLSearchParams();
            params.set('district', state.selectedDistrict);
            if (state.selectedYear !== 'all') params.set('year', state.selectedYear);
            window.history.pushState(null, '', '?' + params.toString());
        }

        updateTrackButtonState();

        // 1. Fetch District Summary (KPIs, YoY)
        fetch(`/api/summary/?district=${distEncoded}&year=${yearEncoded}`)
            .then(r => r.json())
            .then(s => {
                renderKPIs(s);
                updateRadarChart(s);
            }).catch(console.error);

        // 2. Fetch Offenses Bar
        fetch(`/api/offenses/?district=${distEncoded}&year=${yearEncoded}${catParam}&limit=12`)
            .then(r => r.json())
            .then(d => {
                updateOffensesBarChart(d.offenses || []);
            }).catch(console.error);

        // 3. Fetch Category Distribution Donut
        fetch(`/api/categories/?district=${distEncoded}&year=${yearEncoded}`)
            .then(r => r.json())
            .then(c => {
                updateDonutChart(c);
            }).catch(console.error);

        // 4. Fetch Critical Offenses
        fetch(`/api/critical-offenses/?district=${distEncoded}&year=${yearEncoded}`)
            .then(r => r.json())
            .then(cr => {
                updateCriticalChart(cr.critical_offenses || []);
            }).catch(console.error);

        // 5. Fetch Multi-Year Trends (7-year timeline)
        fetch(`/api/trends/?district=${distEncoded}`)
            .then(r => r.json())
            .then(tr => {
                updateTrendLineChart(tr);
                renderAnnualShift(tr);
            }).catch(console.error);

        // 6. Fetch Table
        fetchTableData();

        setTimeout(() => { if (loading) loading.style.display = 'none'; }, 200);
    }

    function setDistrict(districtName) {
        state.selectedDistrict = districtName;

        const districtSelect = document.getElementById('karnatakaDistrictSelect');
        if (districtSelect) districtSelect.value = districtName;

        const heroName = document.getElementById('heroDistrictName');
        const tableName = document.getElementById('tableDistrictName');
        const heroSub = document.getElementById('heroBannerSub');
        if (heroName) heroName.textContent = districtName;
        if (tableName) tableName.textContent = districtName;
        if (heroSub) heroSub.textContent = `${districtName} • Official IPC Crime Heads & 7-Year Multi-Year Analytics (2016–2022 Official Dataset)`;
        document.title = `KCAVP | ${districtName} Crime Intelligence (2016–2022)`;

        document.querySelectorAll('.quick-district-chip').forEach(chip => {
            chip.classList.toggle('active', chip.getAttribute('data-district') === districtName);
        });

        document.querySelectorAll('.district-title-span').forEach(span => {
            span.textContent = districtName;
        });

        syncUIState();
    }

    function setYear(yearVal) {
        state.selectedYear = yearVal;

        const yearSelect = document.getElementById('yearSelect');
        if (yearSelect) yearSelect.value = yearVal;

        document.querySelectorAll('#yearPillsGroup .year-pill').forEach(pill => {
            pill.classList.toggle('active', pill.getAttribute('data-year') === yearVal);
        });

        syncUIState();
    }

    // ==========================================
    // EVENT LISTENERS: PINNED DISTRICT CONTROLS (ISOLATED)
    // ==========================================
    // Hero star button: pins active explorer district to watch deck
    const trackDistrictBtn = document.getElementById('trackDistrictBtn');
    if (trackDistrictBtn) {
        trackDistrictBtn.addEventListener('click', function () {
            setPinnedDistrict(state.selectedDistrict);
        });
    }

    // Cockpit button: pins active explorer district
    const pinCurrentDistrictBtn = document.getElementById('pinCurrentDistrictBtn');
    if (pinCurrentDistrictBtn) {
        pinCurrentDistrictBtn.addEventListener('click', function () {
            setPinnedDistrict(state.selectedDistrict);
        });
    }

    // Navbar pinned shortcut button: scrolls down to cockpit WITHOUT modifying main view
    const prefNavBtn = document.getElementById('preferredDistrictQuickBtn');
    if (prefNavBtn) {
        prefNavBtn.addEventListener('click', function () {
            const deck = document.getElementById('pinnedDistrictDeck');
            if (deck) {
                deck.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // Cockpit dropdown select to independently change pinned district
    const pinnedDeckSelect = document.getElementById('pinnedDistrictSelect');
    if (pinnedDeckSelect) {
        pinnedDeckSelect.value = state.pinnedDistrict;
        pinnedDeckSelect.addEventListener('change', function () {
            setPinnedDistrict(this.value);
        });
    }

    // District dropdown change
    const districtSelect = document.getElementById('karnatakaDistrictSelect');
    if (districtSelect) {
        districtSelect.addEventListener('change', function () {
            setDistrict(this.value);
        });
    }

    // Year dropdown change
    const yearSelect = document.getElementById('yearSelect');
    if (yearSelect) {
        yearSelect.addEventListener('change', function () {
            setYear(this.value);
        });
    }

    // Year pill buttons
    document.querySelectorAll('#yearPillsGroup .year-pill').forEach(pill => {
        pill.addEventListener('click', function () {
            const yr = this.getAttribute('data-year');
            setYear(yr);
        });
    });

    // Quick district chips
    document.querySelectorAll('.quick-district-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            const dist = this.getAttribute('data-district');
            setDistrict(dist);
        });
    });

    // Category filter pills & synchronization
    function applyCategoryFilter(cat) {
        state.selectedCategory = cat || 'all';
        document.querySelectorAll('#categoryPillsGroup .year-pill').forEach(p => {
            p.classList.toggle('active', p.getAttribute('data-category') === state.selectedCategory);
        });

        const distEncoded = encodeURIComponent(state.selectedDistrict);
        const yearEncoded = encodeURIComponent(state.selectedYear);
        const catParam = state.selectedCategory !== 'all' ? `&category=${encodeURIComponent(state.selectedCategory)}` : '';

        fetch(`/api/offenses/?district=${distEncoded}&year=${yearEncoded}${catParam}&limit=12`)
            .then(res => res.json())
            .then(d => {
                updateOffensesBarChart(d.offenses || []);
            }).catch(console.error);

        fetchTableData();
    }

    document.querySelectorAll('#categoryPillsGroup .year-pill').forEach(pill => {
        pill.addEventListener('click', function () {
            const cat = this.getAttribute('data-category');
            applyCategoryFilter(cat);
        });
    });

    // Table search
    const searchInput = document.getElementById('tableSearchInput');
    const tableClearBtn = document.getElementById('tableClearBtn');
    let searchDebounce = null;
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            if (tableClearBtn) {
                tableClearBtn.style.display = this.value ? 'inline-flex' : 'none';
            }
            clearTimeout(searchDebounce);
            searchDebounce = setTimeout(() => {
                state.tableSearch = this.value;
                fetchTableData();
            }, 200);
        });
    }

    if (tableClearBtn && searchInput) {
        tableClearBtn.addEventListener('click', function () {
            searchInput.value = '';
            tableClearBtn.style.display = 'none';
            state.tableSearch = '';
            fetchTableData();
            searchInput.focus();
        });
    }

    // Table sorting
    document.querySelectorAll('#dataTable th[data-sort]').forEach(th => {
        th.addEventListener('click', function () {
            const col = this.getAttribute('data-sort');
            if (state.tableSortBy === col) {
                state.tableSortOrder = (state.tableSortOrder === 'asc' ? 'desc' : 'asc');
            } else {
                state.tableSortBy = col;
                state.tableSortOrder = 'desc';
            }
            fetchTableData();
        });
    });

    // Export District CSV
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function () {
            const url = `/api/export-csv/?district=${encodeURIComponent(state.selectedDistrict)}&year=${encodeURIComponent(state.selectedYear)}`;
            window.location.href = url;
        });
    }

    // Ask KCAVP natural-language query discovery
    const askInput = document.getElementById('askKcavpInput');
    const askBtn = document.getElementById('askKcavpBtn');
    const askBox = document.getElementById('askResultBox');

    function executeQuery(query) {
        if (!query || !query.trim()) return;
        const q = query.toLowerCase().trim();

        if (askBox) {
            askBox.style.display = 'block';
            askBox.innerHTML = `<span style="color: var(--accent-cyan);">Analyzing authentic Karnataka 2016-2022 records...</span>`;
        }

        // Special query: Pinned district check
        if (q.includes('prefer') || q.includes('track') || q.includes('home') || q.includes('pin')) {
            const pinnedDist = state.pinnedDistrict;
            fetch(`/api/summary/?district=${encodeURIComponent(pinnedDist)}&year=all`)
                .then(r => r.json())
                .then(sum => {
                    fetch(`/api/trends/?district=${encodeURIComponent(pinnedDist)}`)
                        .then(r2 => r2.json())
                        .then(tr => {
                            const series = tr.series || [];
                            const last = series[series.length - 1] || {};
                            const first = series[0] || {};
                            const netChg = first.total > 0 ? (((last.total - first.total) / first.total) * 100).toFixed(1) : 0;
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: #fbbf24; font-size: 14px; margin-bottom: 6px;">
                                    ⭐ Continuous Surveillance Deck: ${pinnedDist}
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.6;">
                                    Your pinned district is <strong style="color: #fff;">${pinnedDist}</strong> (monitored autonomously in the Continuous Surveillance Deck with its own gauge & momentum charts).<br>
                                    • Total IPC cases recorded (2016–2022): <strong style="color: #fff;">${formatNumber(sum.total_crimes)}</strong><br>
                                    • Primary threat focus: <strong>${sum.top_offense?.name}</strong> (${formatNumber(sum.top_offense?.count)} cases, ${sum.top_offense?.percentage}% share)<br>
                                    • 7-Year Net Trajectory: <strong>${netChg > 0 ? '+' : ''}${netChg}%</strong> (from ${formatNumber(first.total)} in 2016 to ${formatNumber(last.total)} in 2022).
                                </div>
                            `;
                        });
                });
            return;
        }

        // Detect year in query if specified
        let targetYear = state.selectedYear;
        const yearMatches = ['2022', '2021', '2020', '2019', '2018', '2017', '2016'];
        for (const ym of yearMatches) {
            if (q.includes(ym)) {
                targetYear = ym;
                break;
            }
        }

        fetch(`/api/summary/?district=${encodeURIComponent(state.selectedDistrict)}&year=${encodeURIComponent(targetYear)}`)
            .then(r => r.json())
            .then(summary => {
                fetch(`/api/offenses/?district=${encodeURIComponent(state.selectedDistrict)}&year=${encodeURIComponent(targetYear)}&limit=34`)
                    .then(r2 => r2.json())
                    .then(data => {
                        const offenses = data.offenses || [];
                        const yearNote = targetYear === 'all' ? 'Across 2016–2022' : `In ${targetYear}`;

                        if (q.includes('trend') || q.includes('growth') || q.includes('progression') || q.includes('timeline')) {
                            fetch(`/api/trends/?district=${encodeURIComponent(state.selectedDistrict)}`)
                                .then(r3 => r3.json())
                                .then(trendData => {
                                    const series = trendData.series || [];
                                    const first = series[0] || { total: 0 };
                                    const last = series[series.length - 1] || { total: 0 };
                                    const netChange = first.total > 0 ? (((last.total - first.total) / first.total) * 100).toFixed(1) : 0;
                                    askBox.innerHTML = `
                                        <div style="font-weight: 700; color: #38bdf8; font-size: 14px; margin-bottom: 6px;">
                                            📈 7-Year Crime Trajectory in ${state.selectedDistrict} (2016–2022)
                                        </div>
                                        <div style="color: var(--text-muted); font-size: 13px; line-height: 1.6;">
                                            • <strong>2016 Baseline</strong>: ${formatNumber(first.total)} cases<br>
                                            • <strong>2020 Lockdown</strong>: ${formatNumber(series.find(s=>s.year==='2020')?.total || 0)} cases<br>
                                            • <strong>2022 Latest</strong>: ${formatNumber(last.total)} cases<br>
                                            Net 7-year shift: <strong style="color: #fff;">${netChange > 0 ? '+' : ''}${netChange}%</strong> overall.
                                        </div>
                                    `;
                                });
                            return;
                        }

                        if (q.includes('high') || q.includes('top') || q.includes('most')) {
                            const top1 = offenses[0];
                            const top2 = offenses[1];
                            const top3 = offenses[2];
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: #f8fafc; font-size: 14px; margin-bottom: 6px;">
                                    📌 Highest Recorded Offenses in ${state.selectedDistrict} (${yearNote})
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.5;">
                                    1. <strong>${top1?.name}</strong>: ${formatNumber(top1?.count)} cases (${top1?.percentage}% of district)<br>
                                    2. <strong>${top2?.name}</strong>: ${formatNumber(top2?.count)} cases (${top2?.percentage}%)<br>
                                    3. <strong>${top3?.name}</strong>: ${formatNumber(top3?.count)} cases (${top3?.percentage}%)
                                </div>
                            `;
                            return;
                        }

                        if (q.includes('violent') || q.includes('murder')) {
                            const violentTotal = summary.categories?.violent || 0;
                            const murder = offenses.find(o => o.key === 'murder')?.count || 0;
                            const attMurder = offenses.find(o => o.key === 'attempt_to_commit_murder')?.count || 0;
                            const robbery = offenses.find(o => o.key === 'robbery')?.count || 0;
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: var(--cat-violent); font-size: 14px; margin-bottom: 6px;">
                                    ⚡ Violent Crimes in ${state.selectedDistrict} (${yearNote})
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.5;">
                                    Total violent offenses: <strong style="color: #fff;">${formatNumber(violentTotal)}</strong> (${summary.category_percentages?.violent || 0}% of all crimes in this period).<br>
                                    • Murders: <strong>${formatNumber(murder)}</strong> | Attempt to murder: <strong>${formatNumber(attMurder)}</strong><br>
                                    • Armed Robberies: <strong>${formatNumber(robbery)}</strong>
                                </div>
                            `;
                            return;
                        }

                        if (q.includes('theft') || q.includes('property') || q.includes('burglary')) {
                            const propTotal = summary.categories?.property_economic || 0;
                            const theft = offenses.find(o => o.key === 'theft')?.count || 0;
                            const burglary = offenses.find(o => o.key === 'criminal_trespass_or_burglary')?.count || 0;
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: #60a5fa; font-size: 14px; margin-bottom: 6px;">
                                    💼 Property & Financial Offenses in ${state.selectedDistrict} (${yearNote})
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.5;">
                                    Total property/economic crimes: <strong style="color: #fff;">${formatNumber(propTotal)}</strong> cases (${summary.category_percentages?.property_economic || 0}% of district total).<br>
                                    • Thefts: <strong>${formatNumber(theft)}</strong> cases | Burglaries: <strong>${formatNumber(burglary)}</strong> cases
                                </div>
                            `;
                            return;
                        }

                        if (q.includes('women') || q.includes('child') || q.includes('rape')) {
                            const womenTotal = summary.categories?.women_children || 0;
                            const rape = offenses.find(o => o.key === 'rape')?.count || 0;
                            const assault = offenses.find(o => o.key === 'assault_on_women')?.count || 0;
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: var(--cat-women); font-size: 14px; margin-bottom: 6px;">
                                    🛡️ Women & Child Safety in ${state.selectedDistrict} (${yearNote})
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.5;">
                                    Total safety cases recorded: <strong style="color: #fff;">${formatNumber(womenTotal)}</strong> (${summary.category_percentages?.women_children || 0}% of district crimes).<br>
                                    • Assault on women: <strong>${formatNumber(assault)}</strong> cases | Rape cases: <strong>${formatNumber(rape)}</strong>
                                </div>
                            `;
                            return;
                        }

                        const directMatch = offenses.find(o => o.name.toLowerCase().includes(q) || q.includes(o.name.toLowerCase()));
                        if (directMatch) {
                            askBox.innerHTML = `
                                <div style="font-weight: 700; color: #f8fafc; font-size: 14px; margin-bottom: 6px;">
                                    ${directMatch.icon} ${directMatch.name} in ${state.selectedDistrict} (${yearNote})
                                </div>
                                <div style="color: var(--text-muted); font-size: 13px; line-height: 1.5;">
                                    Recorded cases: <strong style="color: #fff;">${formatNumber(directMatch.count)}</strong> (${directMatch.percentage}% of all crimes in this period).<br>
                                    Classification: <span style="color: ${directMatch.color}; font-weight: 600;">${directMatch.category_label}</span>.
                                </div>
                            `;
                            return;
                        }

                        askBox.innerHTML = `
                            <div style="color: var(--text-muted); font-size: 13px;">
                                In <strong>${state.selectedDistrict}</strong> (${yearNote}), total recorded IPC crimes stand at <strong style="color: #fff;">${formatNumber(summary.total_crimes)}</strong>.<br>
                                Property & economic crimes constitute ${summary.category_percentages?.property_economic || 0}%, traffic safety accounts for ${summary.category_percentages?.public_safety || 0}%, and violent offenses make up ${summary.category_percentages?.violent || 0}%.
                            </div>
                        `;
                    });
            });
    }

    // Expose global helper for inline calls
    window.kcavpSetDistrict = setDistrict;

    if (askBtn && askInput) {
        askBtn.addEventListener('click', () => executeQuery(askInput.value));
        askInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') executeQuery(askInput.value);
        });
    }

    document.querySelectorAll('.ask-chips .chip-btn').forEach(chip => {
        chip.addEventListener('click', function () {
            const prompt = this.getAttribute('data-prompt');
            if (askInput) askInput.value = prompt;
            executeQuery(prompt);
        });
    });

    // ==========================================
    // Clear All / Reset Action
    // ==========================================
    function resetAll() {
        const defaultDistrict = window.KCAVP_DEFAULT_DISTRICT || 'Bengaluru City';

        state.selectedCategory = 'all';
        state.selectedYear = 'all';
        document.querySelectorAll('#categoryPillsGroup .year-pill').forEach(pill => {
            pill.classList.toggle('active', pill.getAttribute('data-category') === 'all');
        });

        document.querySelectorAll('#yearPillsGroup .year-pill').forEach(pill => {
            pill.classList.toggle('active', pill.getAttribute('data-year') === 'all');
        });

        const ySelect = document.getElementById('yearSelect');
        if (ySelect) ySelect.value = 'all';

        state.tableSearch = '';
        state.tableSortBy = 'count';
        state.tableSortOrder = 'desc';
        if (searchInput) searchInput.value = '';
        if (tableClearBtn) tableClearBtn.style.display = 'none';

        if (askInput) askInput.value = '';
        if (askBox) {
            askBox.style.display = 'none';
            askBox.innerHTML = '';
        }

        if (window.history && window.history.pushState) {
            window.history.pushState(null, '', window.location.pathname);
        }

        setDistrict(defaultDistrict);
    }

    const resetAllBtn = document.getElementById('resetAllBtn');
    if (resetAllBtn) {
        resetAllBtn.addEventListener('click', resetAll);
    }

    // =========================================================================
    // KPI CARD INTERACTIVE DEEP-DIVE VISUALIZATION SUITE
    // =========================================================================
    const KPI_META = {
        total: {
            title: 'Total District IPC Crimes — Comprehensive Overview',
            badge: 'District Aggregate',
            icon: '📊',
            color: '#6366f1',
            categoryParam: 'all',
            chart1Title: 'Crime Category Volume Distribution',
            chart1Badge: 'Category Share',
            chart2Title: '7-Year Overall Crime Progression (2016 → 2022)',
            filterBtnLabel: 'View All Categories'
        },
        property_economic: {
            title: 'Property & Financial Crimes — In-Depth Analysis',
            badge: 'Property & Economic',
            icon: '💼',
            color: '#3b82f6',
            categoryParam: 'property_economic',
            chart1Title: 'Property & Economic Offenses Breakdown',
            chart1Badge: 'Category Share',
            chart2Title: 'Property & Theft Annual Trajectory (2016 → 2022)',
            filterBtnLabel: 'Filter Dashboard to Property'
        },
        public_safety: {
            title: 'Traffic & Public Safety Violations — In-Depth Analysis',
            badge: 'Traffic & Safety',
            icon: '🚦',
            color: '#f59e0b',
            categoryParam: 'public_safety',
            chart1Title: 'Traffic & Public Safety Offenses Breakdown',
            chart1Badge: 'Category Share',
            chart2Title: 'Traffic & Public Safety Annual Trajectory (2016 → 2022)',
            filterBtnLabel: 'Filter Dashboard to Traffic & Safety'
        },
        women_children: {
            title: 'Women & Child Safety Offences — Sensitive Surveillance',
            badge: 'Women & Child Safety',
            icon: '🛡️',
            color: '#ec4899',
            categoryParam: 'women_children',
            chart1Title: 'Crimes Against Women & Children Breakdown',
            chart1Badge: 'Sensitive Offenses',
            chart2Title: 'Women & Child Safety Annual Trajectory (2016 → 2022)',
            filterBtnLabel: 'Filter Dashboard to Women & Children'
        },
        violent: {
            title: 'Violent Offenses & Bodily Harm — Deep Threat Analysis',
            badge: 'Violent Crimes',
            icon: '⚠️',
            color: '#f43f5e',
            categoryParam: 'violent',
            chart1Title: 'Violent IPC Offenses Distribution',
            chart1Badge: 'Severe Offenses',
            chart2Title: 'Violent Crimes Annual Trajectory (2016 → 2022)',
            filterBtnLabel: 'Filter Dashboard to Violent Crimes'
        },
        top_offense: {
            title: 'Leading Crime Head Profile — Comparative Hotspot',
            badge: 'Top Offense',
            icon: '🔥',
            color: '#8b5cf6',
            categoryParam: 'all',
            chart1Title: 'Top 6 Recorded IPC Heads Comparison',
            chart1Badge: 'Rank Hierarchy',
            chart2Title: 'Multi-Year Trajectory & Historical Benchmark',
            filterBtnLabel: 'Filter to Leading Category'
        }
    };

    function destroyKpiModalCharts() {
        const c1 = document.getElementById('kpiModalChart1Canvas');
        if (c1 && typeof Chart !== 'undefined') {
            const inst1 = Chart.getChart(c1);
            if (inst1) { try { inst1.destroy(); } catch (e) {} }
        }
        if (kpiModalChart1) {
            try { kpiModalChart1.destroy(); } catch (e) {}
            kpiModalChart1 = null;
        }

        const c2 = document.getElementById('kpiModalChart2Canvas');
        if (c2 && typeof Chart !== 'undefined') {
            const inst2 = Chart.getChart(c2);
            if (inst2) { try { inst2.destroy(); } catch (e) {} }
        }
        if (kpiModalChart2) {
            try { kpiModalChart2.destroy(); } catch (e) {}
            kpiModalChart2 = null;
        }
    }

    function closeKpiModal() {
        const modal = document.getElementById('kpiModal');
        if (modal) modal.style.display = 'none';
        destroyKpiModalCharts();
        currentModalKpiType = null;
    }

    function openKpiModal(kpiType) {
        currentModalKpiType = kpiType;
        const meta = KPI_META[kpiType] || KPI_META.total;
        const modal = document.getElementById('kpiModal');
        if (!modal) return;

        // Show modal backdrop
        modal.style.display = 'flex';

        // Header elements
        const iconEl = document.getElementById('kpiModalIcon');
        if (iconEl) iconEl.textContent = meta.icon;

        const titleEl = document.getElementById('kpiModalTitle');
        if (titleEl) titleEl.textContent = meta.title;

        const badgeEl = document.getElementById('kpiModalCategoryBadge');
        if (badgeEl) {
            badgeEl.textContent = meta.badge;
            badgeEl.style.borderColor = meta.color;
            badgeEl.style.color = meta.color;
        }

        const subEl = document.getElementById('kpiModalSubtitle');
        if (subEl) {
            const yearStr = state.selectedYear === 'all' ? 'cumulative 2016–2022' : `Year ${state.selectedYear}`;
            subEl.textContent = `Comprehensive incident breakdown, multi-year progression, and threat distribution in ${state.selectedDistrict} (${yearStr})`;
        }

        const filterBtn = document.getElementById('kpiModalFilterBtn');
        if (filterBtn) {
            filterBtn.innerHTML = `<span>${meta.filterBtnLabel}</span>`;
            filterBtn.onclick = function () {
                let targetCategory = meta.categoryParam;
                if (kpiType === 'total') targetCategory = 'all';
                applyCategoryFilter(targetCategory);
                closeKpiModal();
            };
        }

        // Telemetry loading states
        const kmTotalCases = document.getElementById('kmTotalCases');
        const kmPeriodSub = document.getElementById('kmPeriodSub');
        const kmSharePct = document.getElementById('kmSharePct');
        const kmNetTrajectory = document.getElementById('kmNetTrajectory');
        const kmTrajectorySub = document.getElementById('kmTrajectorySub');
        const kmTopContributor = document.getElementById('kmTopContributor');
        const kmContributorSub = document.getElementById('kmContributorSub');

        if (kmTotalCases) kmTotalCases.textContent = '...';
        if (kmSharePct) kmSharePct.textContent = '...%';
        if (kmNetTrajectory) kmNetTrajectory.textContent = '...';
        if (kmTopContributor) kmTopContributor.textContent = '...';

        const chart1Head = document.getElementById('kpiModalChart1Heading');
        if (chart1Head) chart1Head.textContent = meta.chart1Title;
        const chart1Badge = document.getElementById('kpiModalChart1Badge');
        if (chart1Badge) chart1Badge.textContent = meta.chart1Badge;

        const chart2Head = document.getElementById('kpiModalChart2Heading');
        if (chart2Head) chart2Head.textContent = meta.chart2Title;

        // Fetch data
        const dist = encodeURIComponent(state.selectedDistrict);
        const yr = encodeURIComponent(state.selectedYear);
        const catParam = meta.categoryParam !== 'all' ? `&category=${encodeURIComponent(meta.categoryParam)}` : '';

        destroyKpiModalCharts();

        Promise.all([
            fetch(`/api/summary/?district=${dist}&year=${yr}`).then(r => r.json()).catch(() => ({})),
            fetch(`/api/trends/?district=${dist}`).then(r => r.json()).catch(() => ({})),
            fetch(`/api/offenses/?district=${dist}&year=${yr}${catParam}&limit=12`).then(r => r.json()).catch(() => ({ offenses: [] }))
        ]).then(([summaryData, trendsData, offensesData]) => {
            if (currentModalKpiType !== kpiType) return; // Stale request guard

            const offenses = offensesData.offenses || [];
            const series = trendsData.series || [];
            const years = trendsData.years || ['2016', '2017', '2018', '2019', '2020', '2021', '2022'];

            // 1. Calculate Telemetry Values
            let totalRecorded = 0;
            let sharePct = 0;
            let topHeadName = '--';
            let topHeadCount = 0;

            if (kpiType === 'total') {
                totalRecorded = summaryData.total_crimes || 0;
                sharePct = 100;
                topHeadName = summaryData.top_offense ? summaryData.top_offense.name : (offenses[0]?.name || 'Total IPC');
                topHeadCount = summaryData.top_offense ? summaryData.top_offense.count : (offenses[0]?.count || 0);
            } else if (kpiType === 'top_offense') {
                totalRecorded = summaryData.top_offense ? summaryData.top_offense.count : (offenses[0]?.count || 0);
                sharePct = summaryData.top_offense ? summaryData.top_offense.percentage : (offenses[0]?.percentage || 0);
                topHeadName = summaryData.top_offense ? summaryData.top_offense.name : (offenses[0]?.name || 'Leading Crime');
                topHeadCount = totalRecorded;
            } else {
                totalRecorded = summaryData[kpiType] || summaryData.categories?.[kpiType] || 0;
                sharePct = summaryData.category_percentages?.[kpiType] || 0;
                if (offenses.length > 0) {
                    topHeadName = offenses[0].name;
                    topHeadCount = offenses[0].count;
                }
            }

            if (kmTotalCases) kmTotalCases.textContent = formatNumber(totalRecorded);
            if (kmPeriodSub) kmPeriodSub.textContent = state.selectedYear === 'all' ? '2016–2022 Total' : `Year ${state.selectedYear}`;
            if (kmSharePct) kmSharePct.textContent = `${sharePct}%`;

            if (kmTopContributor) kmTopContributor.textContent = topHeadName;
            if (kmContributorSub) {
                const headPct = totalRecorded > 0 ? ((topHeadCount / totalRecorded) * 100).toFixed(1) : 0;
                kmContributorSub.textContent = `${formatNumber(topHeadCount)} cases (${headPct}% of group)`;
            }

            // 7-Year Net Trajectory calculation
            let seriesKey = kpiType;
            if (kpiType === 'total') seriesKey = 'total';
            else if (kpiType === 'top_offense') {
                seriesKey = summaryData.top_offense?.key || (offenses[0]?.key) || 'theft';
            }

            const firstYearSeries = series.find(s => s.year === '2016');
            const lastYearSeries = series.find(s => s.year === '2022');
            let y16 = firstYearSeries ? (firstYearSeries[seriesKey] !== undefined ? firstYearSeries[seriesKey] : firstYearSeries.total) : 0;
            let y22 = lastYearSeries ? (lastYearSeries[seriesKey] !== undefined ? lastYearSeries[seriesKey] : lastYearSeries.total) : 0;

            if (y16 > 0) {
                const diff = y22 - y16;
                const pct = ((diff / y16) * 100).toFixed(1);
                const sign = diff >= 0 ? '+' : '';
                const color = diff <= 0 ? '#10b981' : '#f43f5e';
                if (kmNetTrajectory) {
                    kmNetTrajectory.innerHTML = `<span style="color: ${color}; font-weight: 800;">${sign}${pct}%</span>`;
                }
                if (kmTrajectorySub) {
                    kmTrajectorySub.textContent = `2016 (${formatNumber(y16)}) → 2022 (${formatNumber(y22)})`;
                }
            } else {
                if (kmNetTrajectory) kmNetTrajectory.textContent = 'Steady';
                if (kmTrajectorySub) kmTrajectorySub.textContent = 'Multi-year active';
            }

            // 2. Render Chart 1: Breakdown
            renderKpiModalChart1(kpiType, meta, summaryData, offenses);

            // 3. Render Chart 2: 7-Year Trajectory
            renderKpiModalChart2(kpiType, meta, years, series, seriesKey);

            // 4. Populate Offenses Registry Table
            populateKpiModalTable(offenses, totalRecorded);
        }).catch(err => {
            console.error('Error loading KPI modal data:', err);
        });
    }

    function renderKpiModalChart1(kpiType, meta, summary, offenses) {
        const canvas = document.getElementById('kpiModalChart1Canvas');
        if (!canvas) return;

        let labels = [];
        let dataVals = [];
        let bgColors = [];

        if (kpiType === 'total') {
            const catMap = [
                { key: 'property_economic', name: 'Property & Financial', color: '#3b82f6' },
                { key: 'public_safety', name: 'Traffic & Public Safety', color: '#f59e0b' },
                { key: 'women_children', name: 'Women & Child Safety', color: '#ec4899' },
                { key: 'violent', name: 'Violent Offenses', color: '#f43f5e' },
                { key: 'public_order', name: 'Public Order', color: '#8b5cf6' },
                { key: 'other', name: 'Other IPC Crimes', color: '#64748b' }
            ];
            catMap.forEach(c => {
                const count = summary.categories?.[c.key] || 0;
                labels.push(c.name);
                dataVals.push(count);
                bgColors.push(c.color);
            });
        } else if (kpiType === 'top_offense') {
            const topSlice = offenses.slice(0, 6);
            topSlice.forEach((o, i) => {
                labels.push(o.name);
                dataVals.push(o.count);
                bgColors.push(i === 0 ? '#8b5cf6' : 'rgba(139, 92, 246, 0.45)');
            });
        } else {
            offenses.slice(0, 8).forEach(o => {
                labels.push(o.name);
                dataVals.push(o.count);
                bgColors.push(o.color || meta.color);
            });
        }

        const isDark = state.theme === 'dark';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';
        const textColor = isDark ? '#94a3b8' : '#64748b';

        kpiModalChart1 = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cases',
                    data: dataVals,
                    backgroundColor: bgColors,
                    borderRadius: 5,
                    maxBarThickness: 28
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: isDark ? '#f8fafc' : '#0f172a',
                        bodyColor: isDark ? '#cbd5e1' : '#334155',
                        borderColor: meta.color,
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: function (ctx) {
                                const total = dataVals.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                                return ` Cases: ${formatNumber(ctx.raw)} (${pct}% of visible share)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            font: { family: 'JetBrains Mono', size: 10 },
                            callback: function (v) { return v >= 1000 ? (v / 1000) + 'k' : v; }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: textColor, font: { family: 'Inter', size: 11, weight: 500 } }
                    }
                }
            }
        });
    }

    function renderKpiModalChart2(kpiType, meta, years, series, seriesKey) {
        const canvas = document.getElementById('kpiModalChart2Canvas');
        if (!canvas) return;

        const isDark = state.theme === 'dark';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(0, 0, 0, 0.06)';
        const textColor = isDark ? '#94a3b8' : '#64748b';

        // Extract trajectory data points
        const trajectoryData = years.map(yr => {
            const entry = series.find(s => s.year === String(yr));
            if (!entry) return 0;
            if (entry[seriesKey] !== undefined) return entry[seriesKey];
            return entry.total || 0;
        });

        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 240);
        gradient.addColorStop(0, meta.color + '44');
        gradient.addColorStop(1, meta.color + '00');

        kpiModalChart2 = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: meta.badge + ' Annual Cases',
                    data: trajectoryData,
                    borderColor: meta.color,
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointRadius: 5,
                    pointBackgroundColor: meta.color,
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                        titleColor: isDark ? '#f8fafc' : '#0f172a',
                        bodyColor: isDark ? '#cbd5e1' : '#334155',
                        borderColor: meta.color,
                        borderWidth: 1,
                        padding: 10,
                        callbacks: {
                            label: function (ctx) {
                                return ` ${ctx.label}: ${formatNumber(ctx.raw)} cases`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, font: { family: 'JetBrains Mono', size: 10 } }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            font: { family: 'JetBrains Mono', size: 10 },
                            callback: function (v) { return v >= 1000 ? (v / 1000) + 'k' : v; }
                        }
                    }
                }
            }
        });
    }

    function populateKpiModalTable(offenses, totalGroupCases) {
        const tbody = document.getElementById('kpiModalTableBody');
        const countNote = document.getElementById('kmTableCountNote');
        if (!tbody) return;

        if (countNote) {
            countNote.textContent = `Displaying ${offenses.length} detailed IPC offenses`;
        }

        if (!offenses || offenses.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 20px;">No individual offenses recorded for this selection.</td></tr>';
            return;
        }

        tbody.innerHTML = offenses.map(off => {
            const count = off.count || 0;
            const pct = totalGroupCases > 0 ? ((count / totalGroupCases) * 100).toFixed(1) : (off.percentage || 0);

            // Severity badge
            let sevClass = 'km-sev-low';
            let sevText = 'Low / Non-Violent';
            const k = (off.key || '').toLowerCase();
            const c = (off.category || '').toLowerCase();

            if (c === 'violent' || k.includes('murder') || k.includes('rape') || k.includes('pocso') || k.includes('dacoity') || k.includes('robbery') || k.includes('kidnap')) {
                sevClass = 'km-sev-high';
                sevText = 'High / Critical';
            } else if (count > 800 || k.includes('cheating') || k.includes('theft') || k.includes('burglary') || k.includes('rash') || k.includes('negligen')) {
                sevClass = 'km-sev-medium';
                sevText = 'Medium';
            }

            return `
                <tr>
                    <td style="font-weight: 600; color: #fff;">
                        <span style="margin-right: 6px;">${off.icon || '📌'}</span>${off.name}
                    </td>
                    <td>
                        <span style="color: var(--text-muted); font-size: 11px;">${off.category_label || off.category || 'General IPC'}</span>
                    </td>
                    <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--text-primary);">
                        ${formatNumber(count)}
                    </td>
                    <td>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <div style="flex: 1; max-width: 60px; height: 5px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden;">
                                <div style="width: ${Math.min(100, pct)}%; height: 100%; background: var(--primary);"></div>
                            </div>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;">${pct}%</span>
                        </div>
                    </td>
                    <td>
                        <span class="km-severity-pill ${sevClass}">${sevText}</span>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Attach listeners to all 6 KPI cards
    document.querySelectorAll('.kpi-card[data-kpi]').forEach(card => {
        card.addEventListener('click', function () {
            const kpi = this.getAttribute('data-kpi');
            if (kpi) openKpiModal(kpi);
        });
        card.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const kpi = this.getAttribute('data-kpi');
                if (kpi) openKpiModal(kpi);
            }
        });
    });

    // Modal controls: close button, backdrop click, Escape key
    const kpiModal = document.getElementById('kpiModal');
    const kpiCloseBtn = document.getElementById('kpiModalCloseBtn');
    if (kpiCloseBtn) {
        kpiCloseBtn.addEventListener('click', closeKpiModal);
    }
    if (kpiModal) {
        kpiModal.addEventListener('click', function (e) {
            if (e.target === kpiModal) {
                closeKpiModal();
            }
        });
    }
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && kpiModal && kpiModal.style.display !== 'none') {
            closeKpiModal();
        }
    });

    // Mount initial visual charts for main explorer
    initOffensesBarChart(initialOffenses);
    initDonutChart(initialCategories);
    initTrendLineChart(initialTrends);
    renderAnnualShift(initialTrends);
    initCriticalChart(initialCritical);
    initRadarChart(initialSummary);

    // Mount Pinned District surveillance cockpit independently
    setPinnedDistrict(state.pinnedDistrict);
})();