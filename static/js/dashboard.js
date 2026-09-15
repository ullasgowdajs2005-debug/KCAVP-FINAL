/**
 * KCAVP — Karnataka & National Crime Analytics & Visualization Platform
 * Client Application Controller & Chart Engine
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initial data passed from Django template context
    const initialSummary = window.KCAVP_INITIAL_SUMMARY || {};
    const initialTrends = window.KCAVP_INITIAL_TRENDS || [];
    const initialRankings = window.KCAVP_INITIAL_RANKINGS || [];
    const initialCategories = window.KCAVP_INITIAL_CATEGORIES || {};
    const initialTable = window.KCAVP_INITIAL_TABLE || {};

    // Global State
    const state = {
        selectedState: window.KCAVP_DEFAULT_STATE || 'Karnataka',
        selectedYear: window.KCAVP_DEFAULT_YEAR || '2022',
        trendMetric: 'total',
        rankingMetric: 'total',
        tablePage: 1,
        tableSortBy: 'total',
        tableSortOrder: 'desc',
        tableSearch: '',
        theme: localStorage.getItem('kcavp_theme') || 'dark'
    };

    // Chart References
    let trajectoryChart = null;
    let rankingChart = null;
    let donutChart = null;
    let radarChart = null;
    let modalTimelineChart = null;

    // Initialize Theme
    applyTheme(state.theme);

    // Setup Theme Toggle
    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', function () {
            state.theme = state.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('kcavp_theme', state.theme);
            applyTheme(state.theme);
            updateChartsTheme();
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = document.getElementById('themeToggleIcon');
        if (icon) {
            icon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    function updateChartsTheme() {
        if (trajectoryChart) trajectoryChart.update();
        if (rankingChart) rankingChart.update();
        if (donutChart) donutChart.update();
        if (radarChart) radarChart.update();
    }

    // Number formatter utility
    function formatNumber(num) {
        if (num === null || num === undefined) return '0';
        return Number(num).toLocaleString('en-IN');
    }

    // ==========================================
    // 1. KPI Cards Rendering
    // ==========================================
    function renderKPIs(data) {
        if (!data) return;

        // Total Crimes
        const elTotal = document.getElementById('kpiTotalCrimes');
        if (elTotal) animateCounter(elTotal, data.total_crimes || 0);

        // YoY pill
        const elTotalYoY = document.getElementById('kpiTotalYoY');
        if (elTotalYoY) {
            if (data.prev_year) {
                const isUp = data.yoy_growth >= 0;
                elTotalYoY.className = `trend-pill ${isUp ? 'trend-up' : 'trend-down'}`;
                elTotalYoY.innerHTML = `${isUp ? '↑' : '↓'} ${Math.abs(data.yoy_growth)}% YoY`;
            } else {
                elTotalYoY.className = 'trend-pill trend-neutral';
                elTotalYoY.innerHTML = 'Base Year';
            }
        }

        // Violent Crimes
        const elViolent = document.getElementById('kpiViolent');
        if (elViolent) animateCounter(elViolent, data.categories?.violent || 0);

        // Women & Children
        const elWomen = document.getElementById('kpiWomen');
        if (elWomen) animateCounter(elWomen, data.categories?.women_children || 0);

        // Property & Economic
        const elProperty = document.getElementById('kpiProperty');
        if (elProperty) animateCounter(elProperty, data.categories?.property_economic || 0);

        // Public Safety
        const elSafety = document.getElementById('kpiSafety');
        if (elSafety) animateCounter(elSafety, data.categories?.public_safety || 0);

        // Top Hotspot District
        const elHotspot = document.getElementById('kpiHotspotDistrict');
        const elHotspotCount = document.getElementById('kpiHotspotCount');
        if (elHotspot) elHotspot.textContent = data.top_district || 'N/A';
        if (elHotspotCount) elHotspotCount.textContent = `${formatNumber(data.top_district_count || 0)} recorded`;
    }

    function animateCounter(element, target) {
        const start = 0;
        const duration = 700;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (target - start) * easeOut);
            element.textContent = formatNumber(current);

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                element.textContent = formatNumber(target);
            }
        }
        requestAnimationFrame(update);
    }

    // ==========================================
    // 2. Trajectory Chart (2016–2022 Timeline)
    // ==========================================
    function initTrajectoryChart(trends) {
        const ctx = document.getElementById('trajectoryChartCanvas')?.getContext('2d');
        if (!ctx) return;

        const years = trends.map(t => t.year);
        const totals = trends.map(t => t.total);
        const violent = trends.map(t => t.violent);
        const women = trends.map(t => t.women_children);
        const property = trends.map(t => t.property_economic);

        const gradientTotal = ctx.createLinearGradient(0, 0, 0, 300);
        gradientTotal.addColorStop(0, 'rgba(99, 102, 241, 0.35)');
        gradientTotal.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

        trajectoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [
                    {
                        label: 'Total Crimes',
                        data: totals,
                        borderColor: '#6366f1',
                        backgroundColor: gradientTotal,
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#6366f1',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Property & Economic',
                        data: property,
                        borderColor: '#3b82f6',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.35,
                        pointRadius: 3
                    },
                    {
                        label: 'Violent Crimes',
                        data: violent,
                        borderColor: '#f43f5e',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.35,
                        pointRadius: 3
                    },
                    {
                        label: 'Women & Child Safety',
                        data: women,
                        borderColor: '#ec4899',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.35,
                        pointRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#94a3b8',
                            font: { family: 'Inter', size: 12, weight: 600 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.92)',
                        titleColor: '#f8fafc',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function (context) {
                                return ` ${context.dataset.label}: ${formatNumber(context.raw)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'JetBrains Mono', size: 11 },
                            callback: function (val) {
                                return val >= 1000 ? (val / 1000) + 'k' : val;
                            }
                        }
                    }
                }
            }
        });
    }

    function updateTrajectoryChart(trends) {
        if (!trajectoryChart) return;
        trajectoryChart.data.labels = trends.map(t => t.year);
        trajectoryChart.data.datasets[0].data = trends.map(t => t.total);
        trajectoryChart.data.datasets[1].data = trends.map(t => t.property_economic);
        trajectoryChart.data.datasets[2].data = trends.map(t => t.violent);
        trajectoryChart.data.datasets[3].data = trends.map(t => t.women_children);
        trajectoryChart.update();
    }

    // ==========================================
    // 3. District Ranking Bar Chart
    // ==========================================
    function initRankingChart(rankings) {
        const ctx = document.getElementById('rankingChartCanvas')?.getContext('2d');
        if (!ctx) return;

        const labels = rankings.map(r => r.district);
        const data = rankings.map(r => r[state.rankingMetric] || r.total);

        rankingChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Recorded Crimes',
                    data: data,
                    backgroundColor: function (context) {
                        const idx = context.dataIndex;
                        return idx === 0 ? '#6366f1' : (idx < 3 ? '#818cf8' : 'rgba(99, 102, 241, 0.5)');
                    },
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.92)',
                        titleColor: '#f8fafc',
                        bodyColor: '#e2e8f0',
                        callbacks: {
                            label: function (context) {
                                return ` Incidents: ${formatNumber(context.raw)}`;
                            }
                        }
                    }
                },
                onClick: function (evt, elements) {
                    if (elements.length > 0) {
                        const index = elements[0].index;
                        const districtName = rankings[index].district;
                        openDistrictModal(districtName);
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: 'JetBrains Mono', size: 11 },
                            callback: function (val) {
                                return val >= 1000 ? (val / 1000) + 'k' : val;
                            }
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            color: '#e2e8f0',
                            font: { family: 'Inter', size: 11, weight: 500 }
                        }
                    }
                }
            }
        });
    }

    function updateRankingChart(rankings) {
        if (!rankingChart) return;
        rankingChart.data.labels = rankings.map(r => r.district);
        rankingChart.data.datasets[0].data = rankings.map(r => r[state.rankingMetric] || r.total);
        rankingChart.update();
    }

    // ==========================================
    // 4. Category Breakdown Donut Chart
    // ==========================================
    function initDonutChart(catData) {
        const ctx = document.getElementById('donutChartCanvas')?.getContext('2d');
        if (!ctx || !catData.categories) return;

        const labels = catData.categories.map(c => c.label);
        const data = catData.categories.map(c => c.count);
        const colors = catData.categories.map(c => c.color);

        donutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#111827',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.92)',
                        callbacks: {
                            label: function (context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${formatNumber(context.raw)} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });

        renderCategoryLegend(catData.categories);
    }

    function updateDonutChart(catData) {
        if (!donutChart || !catData.categories) return;
        donutChart.data.labels = catData.categories.map(c => c.label);
        donutChart.data.datasets[0].data = catData.categories.map(c => c.count);
        donutChart.data.datasets[0].backgroundColor = catData.categories.map(c => c.color);
        donutChart.update();
        renderCategoryLegend(catData.categories);
    }

    function renderCategoryLegend(categories) {
        const container = document.getElementById('categoryLegendContainer');
        if (!container) return;

        container.innerHTML = categories.map(c => `
            <div class="category-legend-item">
                <div class="category-legend-left">
                    <span class="category-legend-dot" style="background-color: ${c.color}"></span>
                    <span class="category-legend-label" title="${c.label}">${c.label}</span>
                </div>
                <div class="category-legend-right">
                    ${c.percentage}%
                </div>
            </div>
        `).join('');
    }

    // ==========================================
    // 5. Crime Severity Radar Chart
    // ==========================================
    function initRadarChart(categories) {
        const ctx = document.getElementById('radarChartCanvas')?.getContext('2d');
        if (!ctx || !categories.categories) return;

        const labels = categories.categories.map(c => c.label.split(' ')[0]);
        const data = categories.categories.map(c => c.percentage);

        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: `${state.selectedState} Profile`,
                    data: data,
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    borderColor: '#6366f1',
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#6366f1',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return ` Share: ${context.raw}% of crimes`;
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        pointLabels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 11, weight: 600 }
                        },
                        ticks: { display: false }
                    }
                }
            }
        });
    }

    function updateRadarChart(categories) {
        if (!radarChart || !categories.categories) return;
        radarChart.data.labels = categories.categories.map(c => c.label.split(' ')[0]);
        radarChart.data.datasets[0].data = categories.categories.map(c => c.percentage);
        radarChart.data.datasets[0].label = `${state.selectedState} Profile`;
        radarChart.update();
    }

    // ==========================================
    // 6. District Heatmap Grid Rendering
    // ==========================================
    function renderHeatmap(rankings) {
        const container = document.getElementById('heatmapGridContainer');
        if (!container) return;

        if (!rankings || rankings.length === 0) {
            container.innerHTML = '<div style="color: var(--text-muted); padding: 20px;">No district records available.</div>';
            return;
        }

        const counts = rankings.map(r => r.total);
        const max = Math.max(...counts) || 1;
        const min = Math.min(...counts) || 0;

        container.innerHTML = rankings.map(r => {
            const ratio = r.total / max;
            let tierClass = 'tier-low';
            let tierLabel = 'Low';
            let color = 'var(--accent-emerald)';

            if (ratio > 0.6) {
                tierClass = 'tier-severe';
                tierLabel = 'Severe';
                color = 'var(--accent-rose)';
            } else if (ratio > 0.35) {
                tierClass = 'tier-elevated';
                tierLabel = 'Elevated';
                color = 'var(--accent-amber)';
            } else if (ratio > 0.15) {
                tierClass = 'tier-moderate';
                tierLabel = 'Moderate';
                color = 'var(--accent-cyan)';
            }

            return `
                <div class="heatmap-cell" style="--intensity-color: ${color};" onclick="window.openDistrictModal('${r.district}')">
                    <div class="cell-district-name" title="${r.district}">${r.district}</div>
                    <div class="cell-district-stat">
                        <span class="cell-crimes-count">${formatNumber(r.total)}</span>
                        <span class="cell-tier-tag ${tierClass}">${tierLabel}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    // ==========================================
    // 7. Data Explorer Table Rendering
    // ==========================================
    function renderTable(data) {
        const tbody = document.getElementById('dataTableBody');
        const paginationInfo = document.getElementById('tablePaginationInfo');
        const prevBtn = document.getElementById('tablePrevBtn');
        const nextBtn = document.getElementById('tableNextBtn');

        if (!tbody) return;

        if (!data.rows || data.rows.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 24px; color: var(--text-muted);">No records found.</td></tr>';
            if (paginationInfo) paginationInfo.textContent = 'Showing 0 of 0 records';
            return;
        }

        tbody.innerHTML = data.rows.map(row => `
            <tr class="table-row-clickable" onclick="window.openDistrictModal('${row.district}')">
                <td>
                    <div class="district-cell-title">
                        <span>${row.district}</span>
                        <span class="district-cell-action">Details →</span>
                    </div>
                </td>
                <td><span style="color: var(--text-muted);">${row.state}</span></td>
                <td class="num-cell" style="font-weight: 700; color: #818cf8;">${formatNumber(row.total)}</td>
                <td class="num-cell" style="color: var(--cat-violent);">${formatNumber(row.violent)}</td>
                <td class="num-cell" style="color: var(--cat-women);">${formatNumber(row.women_children)}</td>
                <td class="num-cell" style="color: var(--cat-property);">${formatNumber(row.property_economic)}</td>
                <td class="num-cell" style="color: var(--cat-safety);">${formatNumber(row.public_safety)}</td>
                <td class="num-cell">${formatNumber(row.murder)}</td>
            </tr>
        `).join('');

        const startItem = (data.page - 1) * data.page_size + 1;
        const endItem = Math.min(data.page * data.page_size, data.total_rows);
        if (paginationInfo) {
            paginationInfo.textContent = `Showing ${startItem}–${endItem} of ${data.total_rows} districts`;
        }

        if (prevBtn) prevBtn.disabled = (data.page <= 1);
        if (nextBtn) nextBtn.disabled = (data.page >= data.total_pages);
    }

    // ==========================================
    // 8. Global State Refresh & API Fetching
    // ==========================================
    async function refreshDashboard() {
        const loadingIndicator = document.getElementById('globalLoadingIndicator');
        if (loadingIndicator) loadingIndicator.style.display = 'inline-block';

        try {
            // Parallel fetches for optimum response time
            const [summaryRes, trendsRes, rankingsRes, catRes, tableRes] = await Promise.all([
                fetch(`/api/summary/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}`),
                fetch(`/api/trends/?state=${encodeURIComponent(state.selectedState)}`),
                fetch(`/api/districts/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}&metric=${state.rankingMetric}&limit=15`),
                fetch(`/api/categories/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}`),
                fetch(`/api/table/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}&search=${encodeURIComponent(state.tableSearch)}&sort_by=${state.tableSortBy}&order=${state.tableSortOrder}&page=${state.tablePage}&page_size=15`)
            ]);

            const summary = await summaryRes.json();
            const trends = await trendsRes.json();
            const rankings = await rankingsRes.json();
            const categories = await catRes.json();
            const table = await tableRes.json();

            // Update UI elements
            renderKPIs(summary);
            updateTrajectoryChart(trends.trends || []);
            updateRankingChart(rankings.districts || []);
            updateDonutChart(categories);
            updateRadarChart(categories);
            renderHeatmap(rankings.districts || []);
            renderTable(table);

            // Update banner subtitles
            const bannerSub = document.getElementById('heroBannerSub');
            if (bannerSub) {
                bannerSub.textContent = `${state.selectedState} • Year ${state.selectedYear} • District-level IPC Crime Intelligence`;
            }

        } catch (err) {
            console.error('Error refreshing dashboard:', err);
        } finally {
            if (loadingIndicator) loadingIndicator.style.display = 'none';
        }
    }

    // ==========================================
    // 9. District Deep Dive Modal
    // ==========================================
    window.openDistrictModal = async function (districtName) {
        const modal = document.getElementById('districtDetailModal');
        if (!modal) return;

        modal.classList.add('active');
        document.getElementById('modalDistrictTitle').textContent = districtName;
        document.getElementById('modalStateSubtitle').textContent = `Loading intelligence profile for ${districtName}, ${state.selectedState}...`;

        try {
            const res = await fetch(`/api/district-detail/?state=${encodeURIComponent(state.selectedState)}&district=${encodeURIComponent(districtName)}`);
            const data = await res.json();

            if (data.error) {
                document.getElementById('modalStateSubtitle').textContent = data.error;
                return;
            }

            document.getElementById('modalDistrictTitle').textContent = data.district;
            document.getElementById('modalStateSubtitle').textContent = `${data.state} • Safety Rating: ${data.safety_level}`;

            document.getElementById('modalTotalCrimes').textContent = formatNumber(data.latest_stat?.total || 0);
            document.getElementById('modalViolentCrimes').textContent = formatNumber(data.latest_stat?.violent || 0);
            document.getElementById('modalStateAverage').textContent = formatNumber(data.state_avg || 0);

            // Render modal timeline chart
            renderModalTimelineChart(data.timeline || []);

        } catch (err) {
            console.error('Error fetching district profile:', err);
        }
    };

    function renderModalTimelineChart(timeline) {
        const ctx = document.getElementById('modalTimelineCanvas')?.getContext('2d');
        if (!ctx) return;

        if (modalTimelineChart) {
            modalTimelineChart.destroy();
        }

        modalTimelineChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: timeline.map(t => t.year),
                datasets: [
                    {
                        type: 'line',
                        label: 'Total Incidents',
                        data: timeline.map(t => t.total),
                        borderColor: '#6366f1',
                        borderWidth: 3,
                        tension: 0.3,
                        pointRadius: 4,
                        yAxisID: 'y'
                    },
                    {
                        type: 'bar',
                        label: 'Violent Crimes',
                        data: timeline.map(t => t.violent),
                        backgroundColor: '#f43f5e',
                        borderRadius: 4
                    },
                    {
                        type: 'bar',
                        label: 'Property Crimes',
                        data: timeline.map(t => t.property_economic),
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
                    }
                },
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }

    const modalCloseBtn = document.getElementById('modalCloseBtn');
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', function () {
            document.getElementById('districtDetailModal')?.classList.remove('active');
        });
    }

    // Close modal on outside click
    const modalOverlay = document.getElementById('districtDetailModal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function (e) {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('active');
            }
        });
    }

    // ==========================================
    // 10. Ask KCAVP Smart Query Engine
    // ==========================================
    const askInput = document.getElementById('askKcavpInput');
    const askResultBox = document.getElementById('askResultBox');
    const askBtn = document.getElementById('askKcavpBtn');

    function processQuery(query) {
        if (!query || !query.trim()) return;
        const q = query.toLowerCase().trim();
        let answer = '';

        if (q.includes('highest violent') || q.includes('most violent')) {
            const violentSorted = [...initialRankings].sort((a, b) => b.violent - a.violent);
            const top = violentSorted[0];
            answer = `🚨 <strong>Highest Violent Crimes</strong>: <strong>${top.district}</strong> leads in violent offenses with <strong>${formatNumber(top.violent)}</strong> recorded cases in ${state.selectedYear} (${((top.violent / top.total) * 100).toFixed(1)}% of its crime volume).`;
        } else if (q.includes('safest') || q.includes('lowest')) {
            const lowestSorted = [...initialRankings].sort((a, b) => a.total - b.total);
            const safest = lowestSorted[0];
            answer = `🛡️ <strong>Safest District</strong>: <strong>${safest.district}</strong> recorded the lowest crime volume in ${state.selectedState} with just <strong>${formatNumber(safest.total)}</strong> total incidents in ${state.selectedYear}.`;
        } else if (q.includes('women') || q.includes('safety')) {
            const womenSorted = [...initialRankings].sort((a, b) => b.women_children - a.women_children);
            const top = womenSorted[0];
            answer = `🌸 <strong>Crimes Against Women & Children</strong>: Highest volume recorded in <strong>${top.district}</strong> with <strong>${formatNumber(top.women_children)}</strong> cases in ${state.selectedYear}. Statewide, this category represents ~${initialCategories.categories?.find(c => c.id === 'women_children')?.percentage || 10}% of all IPC crimes.`;
        } else if (q.includes('theft') || q.includes('property')) {
            const theftSorted = [...initialRankings].sort((a, b) => b.theft - a.theft);
            const top = theftSorted[0];
            answer = `💼 <strong>Theft & Property Crimes</strong>: <strong>${top.district}</strong> is the primary hotspot with <strong>${formatNumber(top.theft)}</strong> reported theft incidents in ${state.selectedYear}.`;
        } else if (q.includes('trend') || q.includes('overall') || q.includes('trajectory')) {
            const first = initialTrends[0];
            const last = initialTrends[initialTrends.length - 1];
            const change = last && first ? (((last.total - first.total) / first.total) * 100).toFixed(1) : 0;
            answer = `📈 <strong>Multi-Year Trajectory</strong>: Total IPC crimes moved from <strong>${formatNumber(first?.total)}</strong> in 2016 to <strong>${formatNumber(last?.total)}</strong> in 2022 (${change >= 0 ? '+' : ''}${change}% net change over the 7-year timeframe).`;
        } else {
            // Check if district name is mentioned
            const matched = initialRankings.find(r => q.includes(r.district.toLowerCase()));
            if (matched) {
                answer = `📍 <strong>District Intelligence for ${matched.district}</strong>: Recorded <strong>${formatNumber(matched.total)}</strong> total crimes in ${state.selectedYear} (Violent: ${formatNumber(matched.violent)}, Property: ${formatNumber(matched.property_economic)}, Women Safety: ${formatNumber(matched.women_children)}). Click to open full profile.`;
            } else {
                answer = `🔍 Querying datasets for "<em>${query}</em>": Statewide ${state.selectedState} in ${state.selectedYear} records <strong>${formatNumber(initialSummary.total_crimes)}</strong> crimes across ${initialSummary.district_count} districts. Top hotspot: <strong>${initialSummary.top_district}</strong>.`;
            }
        }

        if (askResultBox) {
            askResultBox.innerHTML = answer;
            askResultBox.classList.add('show');
        }
    }

    if (askBtn && askInput) {
        askBtn.addEventListener('click', () => processQuery(askInput.value));
        askInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') processQuery(askInput.value);
        });
    }

    // Query Prompt Chips
    document.querySelectorAll('.chip-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const prompt = this.getAttribute('data-prompt');
            if (askInput) askInput.value = prompt;
            processQuery(prompt);
        });
    });

    // ==========================================
    // 11. Event Listeners for Filters
    // ==========================================
    // State selector
    const stateSelect = document.getElementById('globalStateSelect');
    if (stateSelect) {
        stateSelect.addEventListener('change', function () {
            state.selectedState = this.value;
            state.tablePage = 1;
            refreshDashboard();
        });
    }

    // Year selection pills
    document.querySelectorAll('.year-pill').forEach(pill => {
        pill.addEventListener('click', function () {
            document.querySelectorAll('.year-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            state.selectedYear = this.getAttribute('data-year');
            state.tablePage = 1;
            refreshDashboard();
        });
    });

    // Ranking Metric Filter Buttons
    document.querySelectorAll('.ranking-filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.ranking-filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            state.rankingMetric = this.getAttribute('data-metric');
            fetch(`/api/districts/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}&metric=${state.rankingMetric}&limit=15`)
                .then(r => r.json())
                .then(data => {
                    updateRankingChart(data.districts || []);
                });
        });
    });

    // Table Search
    const tableSearch = document.getElementById('tableSearchInput');
    let debounceTimeout = null;
    if (tableSearch) {
        tableSearch.addEventListener('input', function () {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                state.tableSearch = this.value;
                state.tablePage = 1;
                fetchTableData();
            }, 300);
        });
    }

    // Table Pagination
    const prevBtn = document.getElementById('tablePrevBtn');
    const nextBtn = document.getElementById('tableNextBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (state.tablePage > 1) {
                state.tablePage--;
                fetchTableData();
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            state.tablePage++;
            fetchTableData();
        });
    }

    // Table Sorting
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        th.addEventListener('click', function () {
            const col = this.getAttribute('data-sort');
            if (state.tableSortBy === col) {
                state.tableSortOrder = state.tableSortOrder === 'desc' ? 'asc' : 'desc';
            } else {
                state.tableSortBy = col;
                state.tableSortOrder = 'desc';
            }
            fetchTableData();
        });
    });

    function fetchTableData() {
        fetch(`/api/table/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}&search=${encodeURIComponent(state.tableSearch)}&sort_by=${state.tableSortBy}&order=${state.tableSortOrder}&page=${state.tablePage}&page_size=15`)
            .then(r => r.json())
            .then(data => renderTable(data));
    }

    // Export CSV Button
    const exportBtn = document.getElementById('exportCsvBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function () {
            window.location.href = `/api/export-csv/?state=${encodeURIComponent(state.selectedState)}&year=${state.selectedYear}`;
        });
    }

    // ==========================================
    // 12. Initial Mount Render
    // ==========================================
    renderKPIs(initialSummary);
    initTrajectoryChart(initialTrends);
    initRankingChart(initialRankings);
    initDonutChart(initialCategories);
    initRadarChart(initialCategories);
    renderHeatmap(initialRankings);
    renderTable(initialTable);
});
