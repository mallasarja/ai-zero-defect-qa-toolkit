# Zero Defect Dashboard

A React-based dashboard that displays bug metrics and data from JSON and CSV files.

## Features

- **Summary Cards**: Displays key metrics including total bugs, escaped bugs, PR linked bugs, and average MTTR
- **Bug Data Table**: Shows detailed bug information with filtering and formatting
- **Placeholder Charts**: Ready sections for future analytics and trends
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data Loading**: Dynamically loads data from JSON and CSV files

## Data Sources

The dashboard reads from two files in the `zero-defect-dashboard/` directory:
- `bug_metrics_dashboard.json` - Contains summary metrics
- `bug_with_pr_link.csv` - Contains detailed bug data

## Installation

1. Install dependencies:
```bash
npm install
```

## Running the Dashboard

To start the development server:
```bash
npm run dashboard
```

or 

```bash
npm start
```

The dashboard will open automatically in your browser at `http://localhost:3000`.

## Building for Production

To create a production build:
```bash
npm run build
```

### Production (GitHub Pages)
- Deploys from `main` via `.github/workflows/deploy-dashboard.yml`.
- Output served from `dist/` with `public/` data copied during build.
- Entry: `zero-defect-dashboard/index.js`; static assets under `zero-defect-dashboard/public/`.

## Dashboard Components

### Summary Cards
- **Total Bugs**: Shows the total number of bugs from the metrics JSON
- **Escaped Bugs**: Displays bugs that escaped to production
- **PR Linked Bugs**: Shows bugs that have associated pull requests
- **Average MTTR**: Mean time to resolution in days

### Bug Data Table
Displays the following columns:
- **Bug ID**: Links to the actual bug if URL is provided
- **Title**: Extracted title from bug ID
- **Module**: Component or feature affected
- **Severity**: Priority level with color coding (P1, P2, P3, P4)
- **Linked PR**: Pull request number if available
- **Escaped Defect**: Yes/No indicator with color coding

### Charts Section (Placeholder)
Ready-to-implement sections for:
- Bug Trend Over Time
- Severity Distribution
- Team Performance
- Resolution Time Analysis

## Project Structure

```
src/
├── index.js          # React app entry point
├── index.html        # HTML template
├── Dashboard.js      # Main dashboard component
└── Dashboard.css     # Dashboard styles

Configuration:
├── webpack.config.js # Webpack configuration
├── .babelrc         # Babel configuration
└── package.json     # Dependencies and scripts
```

## Data Format

### JSON Metrics Format
```json
{
  "total_bugs": 762,
  "escaped_bugs": 0,
  "bugs_with_linked_prs": 257,
  "average_mttr_days": 44.28
}
```

### CSV Columns Used
- `Bug Id / Enhancement Id`: Bug identifier
- `Component/Feature`: Module information
- `Priority`: Severity level
- `linked_pr_number`: Associated PR number
- `is_escaped_defect`: Boolean for escaped bugs

## Customization

### Adding New Metrics
1. Update the metrics state in `Dashboard.js`
2. Add new metric cards in the JSX
3. Style new cards in `Dashboard.css`

### Implementing Charts
1. Install a charting library (e.g., Chart.js, Recharts)
2. Replace placeholder sections with actual chart components
3. Process data accordingly for chart consumption

### Styling
- Modify `Dashboard.css` for visual changes
- Uses CSS Grid for responsive layout
- Color scheme can be customized via CSS variables

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Requires JavaScript enabled