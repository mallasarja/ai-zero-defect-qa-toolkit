import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './Dashboard.css';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    total_bugs: 0,
    escaped_bugs: 0,
    pr_linked_bugs: 0,
    avg_mttr: 0
  });
  const [bugData, setBugData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load JSON metrics - adjust path for local files
      const jsonResponse = await fetch('./bug_metrics_dashboard.json');
      if (!jsonResponse.ok) throw new Error('Failed to load metrics data');
      const jsonData = await jsonResponse.json();
      
      setMetrics({
        total_bugs: jsonData.total_bugs,
        escaped_bugs: jsonData.escaped_bugs,
        pr_linked_bugs: jsonData.bugs_with_linked_prs,
        avg_mttr: jsonData.average_mttr_days
      });

      // Load CSV data - adjust path for local files
      const csvResponse = await fetch('./bug_with_pr_link.csv');
      if (!csvResponse.ok) throw new Error('Failed to load bug data');
      const csvText = await csvResponse.text();
      
      Papa.parse(csvText, {
        header: true,
        complete: (results) => {
          // Filter and transform the data to match our required columns
          const transformedData = results.data
            .filter(row => row['Bug Id / Enhancement Id']) // Filter out empty rows
            .map((row, index) => ({
              id: index + 1,
              bugId: row['Bug Id / Enhancement Id'] || '',
              title: extractTitle(row['Bug Id / Enhancement Id']) || 'N/A',
              module: row['Component/Feature'] || 'Unknown',
              severity: row['Priority'] || 'Unknown',
              linkedPrNumber: row['linked_pr_number'] || '',
              isEscapedDefect: row['is_escaped_defect'] === 'True' || row['is_escaped_defect'] === true
            }));
          
          setBugData(transformedData);
          setLoading(false);
        },
        error: (error) => {
          console.error('CSV parsing error:', error);
          setError('Failed to parse CSV data');
          setLoading(false);
        }
      });

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const extractTitle = (bugId) => {
    // Extract a readable title from bug ID - this is a simplified approach
    if (!bugId) return 'N/A';
    if (bugId.includes('https://')) {
      // Extract the bug ID from URL
      const match = bugId.match(/IO-\d+/);
      return match ? match[0] : 'Issue';
    }
    return bugId;
  };

  const formatNumber = (num) => {
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading dashboard data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Zero Defect Dashboard</h1>
        <p>Real-time bug tracking and metrics</p>
      </header>

      {/* Summary Cards */}
      <section className="metrics-section">
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">🐛</div>
            <div className="metric-content">
              <h3>Total Bugs</h3>
              <p className="metric-value">{formatNumber(metrics.total_bugs)}</p>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-icon">🚨</div>
            <div className="metric-content">
              <h3>Escaped Bugs</h3>
              <p className="metric-value">{formatNumber(metrics.escaped_bugs)}</p>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-icon">🔗</div>
            <div className="metric-content">
              <h3>PR Linked Bugs</h3>
              <p className="metric-value">{formatNumber(metrics.pr_linked_bugs)}</p>
            </div>
          </div>
          
          <div className="metric-card">
            <div className="metric-icon">⏱️</div>
            <div className="metric-content">
              <h3>Avg MTTR</h3>
              <p className="metric-value">{metrics.avg_mttr.toFixed(1)} days</p>
            </div>
          </div>
        </div>
      </section>

      {/* Bug Data Table */}
      <section className="table-section">
        <h2>Bug Details</h2>
        <div className="table-container">
          <table className="bug-table">
            <thead>
              <tr>
                <th>Bug ID</th>
                <th>Title</th>
                <th>Module</th>
                <th>Severity</th>
                <th>Linked PR</th>
                <th>Escaped Defect</th>
              </tr>
            </thead>
            <tbody>
              {bugData.slice(0, 50).map((bug) => (
                <tr key={bug.id}>
                  <td>
                    {bug.bugId.includes('https://') ? (
                      <a href={bug.bugId} target="_blank" rel="noopener noreferrer">
                        {extractTitle(bug.bugId)}
                      </a>
                    ) : (
                      bug.bugId
                    )}
                  </td>
                  <td>{bug.title}</td>
                  <td>{bug.module}</td>
                  <td>
                    <span className={`severity-badge severity-${bug.severity.toLowerCase()}`}>
                      {bug.severity}
                    </span>
                  </td>
                  <td>
                    {bug.linkedPrNumber ? (
                      <span className="pr-link">#{bug.linkedPrNumber}</span>
                    ) : (
                      <span className="no-pr">No PR</span>
                    )}
                  </td>
                  <td>
                    <span className={`escaped-badge ${bug.isEscapedDefect ? 'escaped' : 'not-escaped'}`}>
                      {bug.isEscapedDefect ? 'Yes' : 'No'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {bugData.length > 50 && (
            <div className="table-footer">
              Showing first 50 of {bugData.length} bugs
            </div>
          )}
        </div>
      </section>

      {/* Placeholder Charts Section */}
      <section className="charts-section">
        <h2>Analytics & Trends</h2>
        <div className="charts-grid">
          <div className="chart-placeholder">
            <h3>Bug Trend Over Time</h3>
            <div className="placeholder-content">
              <div className="placeholder-icon">📈</div>
              <p>Chart coming soon...</p>
            </div>
          </div>
          
          <div className="chart-placeholder">
            <h3>Severity Distribution</h3>
            <div className="placeholder-content">
              <div className="placeholder-icon">📊</div>
              <p>Chart coming soon...</p>
            </div>
          </div>
          
          <div className="chart-placeholder">
            <h3>Team Performance</h3>
            <div className="placeholder-content">
              <div className="placeholder-icon">👥</div>
              <p>Chart coming soon...</p>
            </div>
          </div>
          
          <div className="chart-placeholder">
            <h3>Resolution Time Analysis</h3>
            <div className="placeholder-content">
              <div className="placeholder-icon">⏰</div>
              <p>Chart coming soon...</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;