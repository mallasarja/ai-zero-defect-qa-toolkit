import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './styles.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Pie, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const DashboardUI = () => {
  // useState to store the extracted metrics
  const [metrics, setMetrics] = useState({
    total_bugs: 0,
    escaped_bugs: 0,
    pr_linked_bugs: 0,
    avg_mttr: 0
  });
  
  const [bugData, setBugData] = useState([]);
  const [filteredBugData, setFilteredBugData] = useState([]);
  const [chartData, setChartData] = useState(null);
  const [severityChartData, setSeverityChartData] = useState(null);
  const [priorityChartData, setPriorityChartData] = useState(null);
  const [releaseBarData, setReleaseBarData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zeroDefectItems, setZeroDefectItems] = useState([]);
  // Removed per request: AI Testing Impact
  const [releaseTrend, setReleaseTrend] = useState([]);
  const [escapedWithoutAi, setEscapedWithoutAi] = useState([]);
  const [invalidCount, setInvalidCount] = useState(0);
  // Removed per request: Automation Coverage and Customer Impact sections
  
  // Filter states
  const [severityFilter, setSeverityFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [escapedFilter, setEscapedFilter] = useState('all');

  // useEffect to fetch both JSON metrics and CSV data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // Compute metrics from CSV to ensure summary matches details
        // (JSON metrics, if present, can lag; so we prefer computed values.)

        // Fetch the enriched CSV file with PR links
        const csvResponse = await fetch(`bug_with_pr_link.csv?t=${Date.now()}`, { cache: 'no-store' });
        if (!csvResponse.ok) {
          throw new Error(`Failed to fetch CSV: ${csvResponse.status}`);
        }
        const csvText = await csvResponse.text();

        // Helpers to detect escaped defects from multiple possible fields
        const parseEscaped = (v) => {
          if (v === undefined || v === null) return false;
          const s = String(v).trim().toLowerCase();
          return s === 'true' || s === 'yes' || s === '1' || s === 'y';
        };
        const isEscaped = (row) => {
          if (parseEscaped(row['is_escaped_defect'])) return true;
          const phase = String(row['Bug Detection Phase'] || row['bug_detection_phase'] || '').toLowerCase();
          if (phase.includes('escaped') || phase.includes('production')) return true;
          const labels = String(row['labels'] || '').toLowerCase();
          if (labels.includes('prod')) return true;
          return false;
        };

        // Parse CSV using PapaParse
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            // Transform rows
            const getField = (row, keys) => {
              for (const k of keys) {
                const v = row[k];
                if (v !== undefined && v !== null && String(v).trim() !== '') return v;
              }
              return '';
            };

            const rows = results.data
              .filter(row => row['issueKey'])
              .map((row, index) => ({
                id: index + 1,
                bugId: row['issueKey'] || '',
                title: getField(row, ['summary','Summary']) || 'N/A',
                module: '-',
                severity: getField(row, ['severity','Severity']) || 'Unknown',
                priority: getField(row, ['priority','Priority']) || getField(row, ['severity','Severity']) || 'Unknown',
                linkedPrNumber: getField(row, ['linked_pr_number','Linked PR Number','linkedPrNumber']) || '',
                isEscapedDefect: isEscaped(row),
                created: getField(row, ['created','Created']) || '',
                resolved: getField(row, ['resolved','Resolved','resolutiondate']) || '',
                status: getField(row, ['status','Status']) || ''
              }));

            setBugData(rows);
            setFilteredBugData(rows);

        // Compute metrics (used if JSON metrics are unavailable)
            const total = rows.length;
            const escaped = rows.reduce((acc, r) => acc + (r.isEscapedDefect ? 1 : 0), 0);
            const prLinked = rows.reduce((acc, r) => acc + (String(r.linkedPrNumber || '').trim() !== '' ? 1 : 0), 0);

            // Average MTTR (days) using created/resolved
            const msPerDay = 1000 * 60 * 60 * 24;
            const durations = rows
              .map(r => {
                const c = r.created ? new Date(r.created) : null;
                const res = r.resolved ? new Date(r.resolved) : null;
                if (!c || !res || isNaN(c.getTime()) || isNaN(res.getTime())) return null;
                return (res.getTime() - c.getTime()) / msPerDay;
              })
              .filter(v => v !== null && isFinite(v) && v >= 0);
            const avgMttr = durations.length ? (durations.reduce((a, b) => a + b, 0) / durations.length) : 0;

            const computedMetrics = {
              total_bugs: total,
              escaped_bugs: escaped,
              pr_linked_bugs: prLinked,
              avg_mttr: avgMttr
            };

            setMetrics(computedMetrics);

            // Zero-Defect monitor: escaped and high-priority (P1/P2 or S1/S2) by either priority or severity
            const normalizeLevel = (val) => {
              const s = String(val || '').trim().toUpperCase();
              if (!s) return '';
              const token = s.split(/[^A-Z0-9]/)[0]; // take first token before space or symbol
              return token;
            };
            const isHighPriority = (r) => {
              const p = normalizeLevel(r.priority);
              const s = normalizeLevel(r.severity);
              return ['P1','P2','S1','S2'].includes(p) || ['P1','P2','S1','S2'].includes(s);
            };
            const zeroDefects = rows.filter(r => r.isEscapedDefect && isHighPriority(r));
            // Show most recent by created date if available
            const zeroDefectsSorted = zeroDefects
              .map(r => ({
                ...r,
                createdTs: r.created ? new Date(r.created).getTime() : 0,
              }))
              .sort((a,b) => b.createdTs - a.createdTs)
              .slice(0, 20);
            setZeroDefectItems(zeroDefectsSorted);

            // Release-wise trend will be set after loading release CSV

            // Build severity distribution
            const sevMap = new Map();
            rows.forEach(r => {
              const s = (r.severity || 'Unknown').toUpperCase();
              sevMap.set(s, (sevMap.get(s) || 0) + 1);
            });
            const sevLabels = Array.from(sevMap.keys());
            const sevData = sevLabels.map(l => sevMap.get(l));
            const sevColors = sevLabels.map(l => mapCategoryToColor(l));

            setSeverityChartData({
              labels: sevLabels.map(l => (l === 'UNKNOWN' ? 'Unknown' : l)),
              datasets: [
                {
                  label: 'Bug Distribution',
                  data: sevData,
                  backgroundColor: sevColors,
                  borderColor: sevColors,
                  borderWidth: 2,
                  hoverOffset: 4,
                  hoverBorderWidth: 3
                }
              ]
            });
            // invalid count (Duplicate/Rejected)
            const invalidStatuses = new Set(['duplicate', 'rejected']);
            setInvalidCount(rows.filter(r => invalidStatuses.has(String(r.status || '').toLowerCase())).length);
          },
          error: (error) => {
            console.error('CSV parsing error:', error);
            setError('Failed to parse CSV data');
          }
        });

      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Optional external insights (non-blocking)
    const fetchOptionalInsights = async () => {
      // Removed: ai_testing_impact.json fetch
      // Removed: automation_coverage.json and customer_impact.json fetches
      try {
        const priResp = await fetch(`bug_priority_distribution.csv?t=${Date.now()}`, { cache: 'no-store' });
        if (priResp.ok) {
          const text = await priResp.text();
          const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
          const labels = parsed.data.map(r => r['priority']);
          const data = parsed.data.map(r => Number(r['count'] || 0));
          const colors = labels.map(l => mapCategoryToColor(l));
          setPriorityChartData({ labels, datasets: [{ data, backgroundColor: colors, borderColor: colors }] });
        }
      } catch (_) {}
      try {
        const relResp = await fetch(`bug_trend_releasewise.csv?t=${Date.now()}`, { cache: 'no-store' });
        if (relResp.ok) {
          const text = await relResp.text();
          const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
          const rows = Array.isArray(parsed.data) ? parsed.data : [];
          // Expected columns: Fix Versions, Severity, Priority, Bug Count (new script)
          const aggByRelease = new Map();
          const byReleaseSeverity = new Map();
          rows.forEach(r => {
            const rel = (r['Fix Versions'] || r['release'] || 'Unknown').trim();
            const sev = (r['Severity'] || '').trim().toUpperCase() || 'UNKNOWN';
            const cnt = Number(r['Bug Count'] || r['count'] || 0) || 0;
            aggByRelease.set(rel, (aggByRelease.get(rel) || 0) + cnt);
            const sevMap = byReleaseSeverity.get(rel) || new Map();
            sevMap.set(sev, (sevMap.get(sev) || 0) + cnt);
            byReleaseSeverity.set(rel, sevMap);
          });
          const releases = Array.from(aggByRelease.keys()).sort();
          const severities = ['S1', 'S2', 'S3', 'S4', 'UNKNOWN'];
          const datasets = severities.map(sev => ({
            label: sev,
            data: releases.map(rel => (byReleaseSeverity.get(rel)?.get(sev) || 0)),
            backgroundColor: mapCategoryToColor(sev),
            borderColor: mapCategoryToColor(sev),
            borderWidth: 1,
            stack: 'severity',
          }));
          setReleaseBarData({ labels: releases, datasets });
          setReleaseTrend(Array.from(aggByRelease.entries()).map(([release, count]) => ({ release, count })));
        }
      } catch (_) {}
      try {
        const escResp = await fetch(`escaped_without_ai_tests.csv?t=${Date.now()}`, { cache: 'no-store' });
        if (escResp.ok) {
          const text = await escResp.text();
          const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
          setEscapedWithoutAi(parsed.data);
        }
      } catch (_) {}
    };
    fetchOptionalInsights();
  }, []);

  // useEffect to filter bug data when filters change
  useEffect(() => {
    if (bugData.length === 0) return;

    let filtered = bugData;

    // Apply severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(bug => 
        (bug.severity || '').toLowerCase() === severityFilter.toLowerCase()
      );
    }

    // Apply escaped defect filter
    if (escapedFilter !== 'all') {
      const isEscaped = escapedFilter === 'true';
      filtered = filtered.filter(bug => bug.isEscapedDefect === isEscaped);
    }

    // Apply priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(bug => 
        (bug.priority || '').toLowerCase() === priorityFilter.toLowerCase()
      );
    }

    // Sort: PR-linked bugs first, then unlinked
    const linked = filtered.filter(b => String(b.linkedPrNumber || '').trim() !== '');
    const notLinked = filtered.filter(b => String(b.linkedPrNumber || '').trim() === '');
    const sorted = [...linked, ...notLinked];

    setFilteredBugData(sorted);
  }, [bugData, severityFilter, priorityFilter, escapedFilter]);

  // Extract title from bug ID (unused for Jira, kept for compatibility)
  const extractTitle = (bugId) => {
    if (!bugId) return 'N/A';
    return bugId;
  };

  // Helper function to format numbers
  const formatNumber = (num) => {
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  // Parse linked PR values from CSV into clickable GitHub links
  const parseLinkedPrs = (value) => {
    if (!value) return [];
    const repo = 'celigo/celigo-qa-automation';
    const parts = String(value)
      .split(/[,;\s]+/)
      .map(s => s.trim())
      .filter(Boolean);
    const items = [];
    for (const p of parts) {
      if (/^https?:\/\//i.test(p)) {
        // URL: try to extract PR number for label
        const m = p.match(/\/(?:pull|pullrequest)\/(\d+)/i);
        const label = m ? `#${m[1]}` : 'PR';
        items.push({ href: p, label });
      } else if (/^\d+$/.test(p)) {
        // Plain PR number
        items.push({ href: `https://github.com/${repo}/pull/${p}`, label: `#${p}` });
      } else if (/^#?\d+$/i.test(p)) {
        const num = p.replace('#', '');
        items.push({ href: `https://github.com/${repo}/pull/${num}`, label: `#${num}` });
      }
    }
    // De-duplicate by href
    const seen = new Set();
    return items.filter(({ href }) => (seen.has(href) ? false : (seen.add(href), true)));
  };

  // Get severity colors
  const getSeverityColor = (severity) => {
    switch ((severity || '').toLowerCase()) {
      case 'p1':
        return { bg: '#fef2f2', text: '#dc2626' };
      case 'p2':
        return { bg: '#fef3c7', text: '#d97706' };
      case 'p3':
        return { bg: '#fef9c3', text: '#ca8a04' };
      case 'p4':
        return { bg: '#f0fdf4', text: '#16a34a' };
      case 's1':
        return { bg: '#fef2f2', text: '#dc2626' };
      case 's2':
        return { bg: '#fef3c7', text: '#d97706' };
      case 's3':
        return { bg: '#fef9c3', text: '#ca8a04' };
      case 's4':
        return { bg: '#f0fdf4', text: '#16a34a' };
      default:
        return { bg: '#f8fafc', text: '#64748b' };
    }
  };
  // Unified palette for pie charts (Severity/Priority)
  const mapCategoryToColor = (label) => {
    const v = String(label || '').trim().toUpperCase();
    if (v === 'P1' || v === 'S1') return '#dc2626'; // red
    if (v === 'P2' || v === 'S2') return '#ea580c'; // orange
    if (v === 'P3' || v === 'S3') return '#ca8a04'; // yellow
    if (v === 'P4' || v === 'S4') return '#16a34a'; // green
    if (v === 'UNKNOWN' || v === 'UNSPECIFIED' || v === 'NOT SET') return '#6b7280';
    return '#64748b';
  };


  // Get Tailwind severity badge classes
  const getSeverityBadgeClass = (severity) => {
    switch ((severity || '').toLowerCase()) {
      case 'p1':
        return 'bg-red-100 text-red-800';
      case 'p2':
        return 'bg-orange-100 text-orange-800';
      case 'p3':
        return 'bg-yellow-100 text-yellow-800';
      case 'p4':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get unique severity values for filter dropdown
  const getUniqueSeverities = () => {
    if (bugData.length === 0) return [];
    const severities = [...new Set(bugData.map(bug => bug.severity))];
    return severities.filter(severity => severity && severity !== 'Unknown').sort();
  };

  // Get unique priority values for filter dropdown
  const getUniquePriorities = () => {
    if (bugData.length === 0) return [];
    const priorities = [...new Set(bugData.map(bug => bug.priority))];
    return priorities.filter(p => p && p !== 'Unknown').sort();
  };

  // Export filtered data to CSV
  const exportToCSV = () => {
    if (filteredBugData.length === 0) {
      alert('No data to export. Please adjust your filters or check if data has loaded.');
      return;
    }

    // CSV headers
    const headers = ['Bug ID', 'Title', 'Module', 'Severity', 'Linked PR Number', 'Is Escaped Defect'];
    
    // Convert filtered data to CSV format
    const csvData = filteredBugData.map(bug => [
      bug.bugId,
      `"${bug.title.replace(/"/g, '""')}"`, // Escape quotes in title
      `"${bug.module.replace(/"/g, '""')}"`, // Escape quotes in module
      bug.severity,
      bug.linkedPrNumber || '',
      bug.isEscapedDefect ? 'Yes' : 'No'
    ]);

    // Combine headers and data
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => row.join(','))
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    
    // Generate filename with timestamp and filter info
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filterInfo = (severityFilter !== 'all' || escapedFilter !== 'all') ? '_filtered' : '';
    const filename = `bug_data${filterInfo}_${timestamp}.csv`;
    
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Chart configuration options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 12,
            weight: '600'
          },
          color: '#374151'
        }
      },
      title: {
        display: true,
        text: 'Bug Trend Over Time',
        font: {
          size: 16,
          weight: '700'
        },
        color: '#111827',
        padding: {
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `${context.parsed.y} bugs`;
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Month',
          font: {
            size: 12,
            weight: '600'
          },
          color: '#6b7280'
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280',
          maxRotation: 45
        },
        grid: {
          display: false
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Number of Bugs',
          font: {
            size: 12,
            weight: '600'
          },
          color: '#6b7280'
        },
        ticks: {
          font: {
            size: 11
          },
          color: '#6b7280',
          beginAtZero: true
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    }
  };

  // Pie chart configuration options
  const severityChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          font: {
            size: 11,
            weight: '600'
          },
          color: '#374151',
          padding: 15,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      title: {
        display: true,
        text: 'Bug Distribution by Severity',
        font: {
          size: 16,
          weight: '700'
        },
        color: '#111827',
        padding: {
          bottom: 20
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#3b82f6',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            return `${context.label}: ${context.parsed} bugs (${percentage}%)`;
          }
        }
      }
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <div className="flex items-center">
            <div className="text-red-500 mr-3">⚠️</div>
            <div>
              <h3 className="text-red-800 font-semibold">Error Loading Dashboard</h3>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-10 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-8 px-6 rounded-2xl shadow-lg">
          <h1 className="text-4xl font-bold mb-2">Bug Metrics Dashboard</h1>
          <p className="text-lg opacity-90">Real-time tracking and analytics</p>
        </header>

        {/* Summary Cards - 2x2 Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <div className="metric-card">
            <div className="metric-icon">🐛</div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">Total Bugs</h3>
              <p className="text-3xl font-bold text-gray-900">{formatNumber(metrics.total_bugs)}</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🚨</div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">Escaped Bugs</h3>
              <p className="text-3xl font-bold text-gray-900">{formatNumber(metrics.escaped_bugs)}</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">🔗</div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">PR Linked Bugs</h3>
              <p className="text-3xl font-bold text-gray-900">{formatNumber(metrics.pr_linked_bugs)}</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">⏱️</div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-2">Avg MTTR</h3>
              <p className="text-3xl font-bold text-gray-900">{metrics.avg_mttr.toFixed(1)} days</p>
            </div>
          </div>
        </div>

        {/* Charts Section - Side by Side */}
        {(chartData || severityChartData || priorityChartData || releaseBarData) && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Analytics & Insights</h2>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {chartData && (
                <div className="chart-container">
                  <Line data={chartData} options={chartOptions} />
                </div>
              )}
              {severityChartData && (
                <div className="chart-container">
                  <Pie data={severityChartData} options={severityChartOptions} />
                </div>
              )}
              {priorityChartData && (
                <div className="chart-container">
                  <Pie data={priorityChartData} options={{ ...severityChartOptions, plugins: { ...severityChartOptions.plugins, title: { ...severityChartOptions.plugins.title, text: 'Bug Distribution by Priority' } } }} />
                </div>
              )}
              {releaseBarData && (
                <div className="chart-container">
                  <Bar
                    data={releaseBarData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: 'Release-wise Bugs (stacked by Severity)' },
                        tooltip: { mode: 'index', intersect: false },
                      },
                      scales: {
                        x: { stacked: true, ticks: { maxRotation: 45, autoSkip: true }, title: { display: true, text: 'Fix Versions' } },
                        y: { stacked: true, beginAtZero: true, title: { display: true, text: 'Bug Count' } },
                      },
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Zero-Defect Monitor */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Zero-Defect Monitor (Escaped P1/P2 by Priority)</h2>
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100 text-gray-700">
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Bug ID</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Title</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Severity</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Created</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {zeroDefectItems.length === 0 && (
                    <tr><td className="px-4 py-3 text-sm text-gray-500" colSpan="5">No escaped P1/P2 defects found.</td></tr>
                  )}
                  {zeroDefectItems.map(item => (
                    <tr key={item.id} className="border-t border-gray-200">
                      <td className="px-4 py-3 text-sm">{item.bugId}</td>
                      <td className="px-4 py-3 text-sm">{item.title}</td>
                      <td className="px-4 py-3 text-sm">{item.severity}</td>
                      <td className="px-4 py-3 text-sm">{item.created || '-'}</td>
                      <td className="px-4 py-3 text-sm">{item.status || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Insights panel removed as requested */}

        {/* Bug Data Table - Full Width */}
        <div className="w-full">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Bug Details</h2>

          {/* Filter Controls */}
          <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center space-x-2">
                <label htmlFor="severity-filter" className="text-sm font-medium text-gray-700">Severity:</label>
                <select
                  id="severity-filter"
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Severities</option>
                  {getUniqueSeverities().map((severity) => (
                    <option key={severity} value={severity}>{severity}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <label htmlFor="priority-filter" className="text-sm font-medium text-gray-700">Priority:</label>
                <select
                  id="priority-filter"
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Priorities</option>
                  {getUniquePriorities().map((priority) => (
                    <option key={priority} value={priority}>{priority}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-2">
                <label htmlFor="escaped-filter" className="text-sm font-medium text-gray-700">Escaped Defect:</label>
                <select
                  id="escaped-filter"
                  value={escapedFilter}
                  onChange={(e) => setEscapedFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All</option>
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>

              <div className="flex items-center space-x-4 ml-auto">
                <span className="text-sm text-gray-600">Showing {filteredBugData.length} bugs</span>
                <span className="text-sm text-gray-500">Invalid (Duplicate/Rejected): {invalidCount}</span>
              </div>
            </div>
          </div>

          <div className="table-container">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Bug ID</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Title</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Priority</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Severity</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Linked PR</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Escaped Defect</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Created</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Resolved</th>
                    <th className="px-4 py-4 text-left text-xs font-semibold uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white">
                  {(() => {
                    const hasLinked = (b) => String(b.linkedPrNumber || '').trim() !== '';
                    const linkedRows = filteredBugData.filter(hasLinked);
                    const notLinkedRows = filteredBugData.filter(b => !hasLinked(b));

                    const renderRow = (bug) => (
                      <tr key={bug.id} className="border-b border-gray-200 hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-sm">{bug.bugId}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{bug.title}</td>
                        <td className="px-4 py-3 text-sm">
                          <span className="severity-badge" style={{ backgroundColor: getSeverityColor(bug.priority).bg, color: getSeverityColor(bug.priority).text }}>
                            {bug.priority}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className="severity-badge" style={{ backgroundColor: getSeverityColor(bug.severity).bg, color: getSeverityColor(bug.severity).text }}>
                            {bug.severity}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {(() => {
                            const prs = parseLinkedPrs(bug.linkedPrNumber);
                            if (prs.length === 0) {
                              return (<span className="text-gray-400 italic text-xs">No PR</span>);
                            }
                            return (
                              <span className="space-x-2">
                                {prs.map((pr, idx) => (
                                  <a key={`${pr.href}-${idx}`} href={pr.href} target="_blank" rel="noopener noreferrer" className="pr-badge underline text-blue-600">{pr.label}</a>
                                ))}
                              </span>
                            );
                          })()}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`escaped-badge ${bug.isEscapedDefect ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>{bug.isEscapedDefect ? 'Yes' : 'No'}</span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{bug.created || '-'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{bug.resolved || '-'}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">{bug.status || '-'}</td>
                      </tr>
                    );

                    return (
                      <>
                        {linkedRows.map(renderRow)}
                        {(linkedRows.length > 0 && notLinkedRows.length > 0) && (
                          <tr key="separator-no-pr" className="bg-gray-50 border-t border-b">
                            <td colSpan="9" className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wider">No PR Linked Bugs</td>
                          </tr>
                        )}
                        {notLinkedRows.map(renderRow)}
                      </>
                    );
                  })()}
                </tbody>
              </table>
            </div>
            {filteredBugData.length === 0 && bugData.length > 0 && (
              <div className="px-6 py-4 text-center text-sm text-gray-600 bg-gray-50 border-t border-gray-200">
                No bugs match the selected filters. Try adjusting your filter criteria.
              </div>
            )}
          </div>
        </div>

        {/* Release trend and escaped without automated tests */}
        <div className="mb-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <h3 className="text-lg font-semibold mb-3">Release-wise Trend</h3>
            <div className="max-h-64 overflow-y-auto">
              <table className="w-full text-xs">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-2 text-left">Release</th>
                    <th className="px-2 py-2 text-right">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {releaseTrend.length === 0 && (<tr><td className="px-2 py-2 text-sm text-gray-500" colSpan="2">No release data.</td></tr>)}
                  {releaseTrend.map((r, idx) => (
                    <tr key={`${r.release || 'Unknown'}-${idx}`} className="border-t">
                      <td className="px-2 py-1">{r.release || 'Unknown'}</td>
                      <td className="px-2 py-1 text-right">{r.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <h3 className="text-lg font-semibold mb-3">Escaped Bugs Without Automated Tests</h3>
            <div className="max-h-64 overflow-y-auto">
              <table className="w-full text-xs">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-2 py-2 text-left">Issue</th>
                    <th className="px-2 py-2 text-left">Summary</th>
                    <th className="px-2 py-2 text-left">Priority</th>
                    <th className="px-2 py-2 text-left">Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {escapedWithoutAi.length === 0 && (<tr><td className="px-2 py-2 text-sm text-gray-500" colSpan="4">None found.</td></tr>)}
                  {escapedWithoutAi.slice(0, 50).map((r, idx) => (
                    <tr key={`${r.issueKey}-${idx}`} className="border-t">
                      <td className="px-2 py-1">{r.issueKey}</td>
                      <td className="px-2 py-1">{r.summary}</td>
                      <td className="px-2 py-1">{r.priority}</td>
                      <td className="px-2 py-1">{r.severity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardUI;
