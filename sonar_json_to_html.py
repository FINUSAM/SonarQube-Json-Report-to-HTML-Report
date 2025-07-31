import json
from collections import Counter, defaultdict

with open('sonar-issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

issues = data.get('issues', [])

# Define severity order for sorting
severity_order = {
    'BLOCKER': 1,
    'CRITICAL': 2,
    'MAJOR': 3,
    'MINOR': 4,
    'INFO': 5
}

all_severities = ['BLOCKER', 'CRITICAL', 'MAJOR', 'MINOR', 'INFO']

def get_severity_rank(sev):
    return severity_order.get(sev.upper(), 99)

def get_line(issue):
    tr = issue.get('textRange', {})
    start_line = tr.get('startLine')
    end_line = tr.get('endLine')
    start_offset = tr.get('startOffset')
    end_offset = tr.get('endOffset')
    
    if start_line and end_line:
        if start_line == end_line:
            if start_offset is not None and end_offset is not None:
                return f"{start_line}:{start_offset} - {end_line}:{end_offset}"
            else:
                return str(start_line)
        else:
            if start_offset is not None and end_offset is not None:
                return f"{start_line}:{start_offset} - {end_line}:{end_offset}"
            else:
                return f"{start_line}-{end_line}"
    elif start_line:
        if start_offset is not None and end_offset is not None:
            return f"{start_line}:{start_offset} - {start_line}:{end_offset}"
        else:
            return str(start_line)
    else:
        return '-'

def format_date(dt):
    return dt.replace('T', ' ').split('+')[0] if dt else '-'

def html_escape(text):
    return (str(text)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))

# Sort issues by severity, then type, then status
issues_sorted = sorted(
    issues,
    key=lambda x: (
        get_severity_rank(x.get('severity', '')),
        x.get('type', ''),
        x.get('status', '')
    )
)

# Group issues by status and then by severity
open_issues_by_sev = defaultdict(list)
closed_issues_by_sev = defaultdict(list)
for issue in issues_sorted:
    status = issue.get('status', '').upper()
    sev = issue.get('severity', '-').upper()
    if status == 'OPEN':
        open_issues_by_sev[sev].append(issue)
    elif status == 'CLOSED':
        closed_issues_by_sev[sev].append(issue)

# Summary counts
severity_counts = Counter(issue.get('severity', '-') for issue in issues if issue.get('status', '').upper() == 'OPEN')
type_counts = Counter(issue.get('type', '-') for issue in issues if issue.get('status', '').upper() == 'OPEN')
status_counts = Counter(issue.get('status', '-') for issue in issues)
total_issues = len(issues)

# CSS for styling
css = '''
<style>
/* Professional CSS Reset and Base Styles */
* {
  box-sizing: border-box;
}

body { 
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
  margin: 0;
  background: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

/* Container for better layout */
.container {
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1em;
}

h1 { 
  color: #2c3e50; 
  font-size: 2.2em; 
  margin-bottom: 0.5em; 
  text-align: center;
  font-weight: 600;
}

/* Professional Summary Card */
.summary-card { 
  background: #f8f9fa; 
  border: 1px solid #dee2e6; 
  border-radius: 8px; 
  padding: 1.5em 2em; 
  margin-bottom: 2em; 
}

.summary-title { 
  font-size: 1.3em; 
  color: #2c3e50; 
  margin-bottom: 1em; 
  font-weight: 600; 
  text-align: center;
}

.summary-row { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 1em; 
  margin-bottom: 0.8em; 
  align-items: center;
}

.summary-label { 
  font-weight: 600; 
  color: #495057; 
  margin-right: 0.8em; 
  font-size: 1em;
}

/* Professional Badges */
.badge { 
  display: inline-block; 
  padding: 0.4em 0.8em; 
  border-radius: 4px; 
  font-size: 0.85em; 
  font-weight: 500; 
  margin-right: 0.4em; 
  margin-bottom: 0.3em; 
  border: 1px solid;
}

.badge-MINOR { background: #e3f2fd; color: #1976d2; border-color: #bbdefb; }
.badge-MAJOR { background: #fff3e0; color: #f57c00; border-color: #ffcc02; }
.badge-CRITICAL { background: #ffebee; color: #d32f2f; border-color: #ffcdd2; }
.badge-BLOCKER { background: #d32f2f; color: white; border-color: #d32f2f; }
.badge-INFO { background: #f5f5f5; color: #616161; border-color: #e0e0e0; }
.badge-CODE_SMELL { background: #f3e5f5; color: #7b1fa2; border-color: #e1bee7; }
.badge-BUG { background: #ffebee; color: #c62828; border-color: #ffcdd2; }
.badge-VULNERABILITY { background: #fff8e1; color: #ef6c00; border-color: #ffecb3; }
.badge-OPEN { background: #e8f5e8; color: #2e7d32; border-color: #c8e6c9; }
.badge-CLOSED { background: #f5f5f5; color: #616161; border-color: #e0e0e0; }

.summary-table { display: none; }

/* Professional Issues Card */
.issues-card { 
  background: white; 
  border: 1px solid #dee2e6; 
  border-radius: 8px; 
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); 
  padding: 1.5em; 
  margin-bottom: 2em; 
  overflow-x: auto;
}

/* Professional Table Styling */
table.issues-table { 
  border-collapse: collapse; 
  width: 100%; 
  margin-top: 0.5em; 
  background: white;
  border: 1px solid #dee2e6;
}

table.issues-table th, 
table.issues-table td { 
  padding: 12px 16px; 
  border: 1px solid #dee2e6; 
  text-align: left;
  font-size: 0.9em;
  vertical-align: top;
}

table.issues-table th { 
  background: #f8f9fa; 
  color: #495057; 
  font-size: 0.9em; 
  font-weight: 600;
  position: sticky; 
  top: 0; 
  z-index: 10; 
  border-bottom: 2px solid #dee2e6;
}

table.issues-table tr { 
  border-bottom: 1px solid #dee2e6;
}

table.issues-table tr:hover { 
  background: #f8f9fa; 
}

table.issues-table tr:nth-child(even) { 
  background: #fafbfc; 
}

table.issues-table tr:nth-child(even):hover {
  background: #f1f3f4;
}

td .badge, 
th .badge { 
  margin-right: 0.3em; 
  margin-bottom: 0.2em; 
  font-size: 0.8em;
}

td .tag { 
  margin-bottom: 0; 
}

/* Professional Tags */
.tag { 
  display: inline-block; 
  background: #e9ecef; 
  color: #495057; 
  border-radius: 3px; 
  padding: 2px 8px; 
  margin-right: 4px; 
  font-size: 0.8em; 
  font-weight: 500;
  border: 1px solid #dee2e6;
}

/* Column Widths and Text Handling */
.issues-table td:nth-child(1) { width: 50px; text-align: center; font-weight: 600; }
.issues-table td:nth-child(2) { width: 180px; }
.issues-table td:nth-child(3) { width: 140px; font-family: 'Courier New', monospace; }
.issues-table td:nth-child(4) { 
  min-width: 280px; 
  max-width: 350px; 
  white-space: pre-line; 
  word-break: break-word;
  line-height: 1.4;
}
.issues-table td:nth-child(5) { 
  max-width: 200px; 
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 0.85em;
}
.issues-table td:nth-child(6) { width: 70px; text-align: center; }
.issues-table td:nth-child(7) { width: 100px; }
.issues-table td:nth-child(8) { width: 100px; }
.issues-table td:nth-child(9) { width: 100px; }
.issues-table td:nth-child(10) { width: 100px; }
.issues-table td:nth-child(11) { width: 120px; }
.issues-table td:nth-child(12) { width: 80px; }
.issues-table td:nth-child(13) { width: 80px; }

/* Professional Details Sections */
.details-modern {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1.5em;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.details-modern[open] {
  background: white;
}

.details-modern > summary {
  font-size: 1.1em;
  font-weight: 600;
  color: #495057;
  cursor: pointer;
  padding: 1em 1.5em;
  outline: none;
  border: none;
  background: none !important;
  border-bottom: 1px solid #dee2e6;
  transition: background-color 0.2s ease;
}

.details-modern > summary:hover {
  background: none !important;
}

.details-modern details {
  margin-left: 0;
  margin-top: 0;
}

.details.details-modern {
    padding: 1.2em 2em;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .container {
    padding: 1em;
  }
  
  table.issues-table {
    font-size: 0.85em;
  }
  
  table.issues-table th, 
  table.issues-table td { 
    padding: 8px 12px; 
  }
}

@media (max-width: 768px) {
  body {
    padding: 1em;
  }
  
  .summary-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .badge {
    margin-bottom: 0.3em;
  }
}

/* Professional typography */
.issues-table td {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.4;
}

/* New styles for issue cards */
.issues-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5em;
    padding: 0.5em;
}

.issue-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5em;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    gap: 0.8em;
}

.issue-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.8em;
    border-bottom: 1px dashed #dee2e6;
    padding-bottom: 0.8em;
    gap: 1em;
}

.issue-number {
    font-size: 1.2em;
    font-weight: 600;
    color: #2c3e50;
    background: #e0e0e0;
    padding: 0.3em 0.8em;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}

.issue-badges {
    display: flex;
    gap: 0.5em;
    align-items: center;
    flex-wrap: wrap;
}

.issue-content {
    flex-grow: 1;
}

.issue-message {
    font-size: 1.1em;
    color: #333;
    line-height: 1.5;
    margin-bottom: 0.8em;
    padding-bottom: 0.8em;
    border-bottom: 1px dashed #dee2e6;
}

.issue-details {
    display: flex;
    flex-direction: column;
    gap: 0.6em;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5em;
    padding: 0.25em 0;
    border-bottom: 1px solid #e9ecef;
}

.detail-label {
    font-weight: 600;
    color: #495057;
    font-size: 0.9em;
    min-width: 60px; /* Ensure labels don't shrink too much */
}

.detail-value {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    color: #555;
    word-break: break-word;
    max-width: 70%;
    text-align: right;
    flex-shrink: 1;
}

.rule-code {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 0.2em 0.5em;
    border-radius: 4px;
    border: 1px solid #e1bee7;
}

.component-path {
    color: #1976d2;
    text-decoration: none;
    cursor: pointer;
}

.component-path:hover {
    text-decoration: underline;
}

.line-info {
    font-size: 0.9em;
    color: #666;
}

.issue-tags {
    margin-top: 0.8em;
    padding-top: 0.8em;
    border-top: 1px dashed #dee2e6;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5em;
    max-width: 70%;
    text-align: right;
    flex-shrink: 1;
}

.no-tags {
    color: #999;
    font-style: italic;
}

</style>
'''

# HTML summary section

def summary_badges(counter, badge_prefix, order=None):
    if order:
        items = [(k, counter.get(k, 0)) for k in order]  # Always include all keys in order, even if count is zero
        # Add any remaining keys not in order
        items += [(k, v) for k, v in counter.items() if k not in order]
    else:
        items = list(counter.items())
    return ' '.join(f'<span class="badge badge-{badge_prefix}{k.replace("_", "-")}">{k}: {v}</span>' for k, v in items)

severity_order = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
type_order = ["BUG", "VULNERABILITY", "CODE_SMELL"]
status_order = ["OPEN", "CLOSED"]

summary_html = f'''
<div class="summary-card">
  <h1>Sonar Issues Report</h1>
  <div class="summary-title">Total Issues: <span style="color:#0f172a">{total_issues}</span></div>
  <div class="summary-row"><span class="summary-label">Severity</span> {summary_badges(severity_counts, '', severity_order)}</div>
  <div class="summary-row"><span class="summary-label">Type</span> {summary_badges(type_counts, '', type_order)}</div>
  <div class="summary-row"><span class="summary-label">Status</span> {summary_badges(status_counts, '', status_order)}</div>
</div>
'''

# HTML table of issues
def issues_table(issues, status_label, severity_label, show_closed_column=True):
    header = '''
    <tr>
      <th>#</th>
      <th>Details</th>
      <th>Rule</th>
      <th>Message</th>
      <th>Component</th>
      <th>Line</th>
      <th>Author</th>
      <th>Created</th>
      <th>Updated</th>''' + ('''
      <th>Closed</th>''' if show_closed_column else '') + '''
      <th>Tags</th>
      <th>Effort</th>
      <th>Debt</th>
    </tr>
    '''
    rows = []
    for i, issue in enumerate(issues, 1):
        sev = issue.get('severity', '-')
        typ = issue.get('type', '-')
        stat = issue.get('status', '-')
        row = f'<tr>'
        row += (
            f'<td>{i}</td>'
            f'<td>'
            f'<span class="badge badge-{sev}">{sev}</span> '
            f'<span class="badge badge-{typ}">{html_escape(typ)}</span> '
            f'<span class="badge badge-{stat}">{html_escape(stat)}</span>'
            f'</td>'
        )
        row += f'<td>{html_escape(issue.get("rule", "-"))}</td>'
        row += f'<td>{html_escape(issue.get("message", "-"))}</td>'
        component = issue.get("component", "-")
        if component != "-":
            if ":" in component:
                component = component.split(":")[-1]
            component = component.replace("src/main/java/", "").replace("src/test/java/", "")
        row += f'<td title="{html_escape(issue.get("component", "-"))}">{html_escape(component)}</td>'
        row += f'<td>{get_line(issue)}</td>'
        row += f'<td>{html_escape(issue.get("author", "-"))}</td>'
        row += f'<td>{format_date(issue.get("creationDate", "-"))}</td>'
        row += f'<td>{format_date(issue.get("updateDate", "-"))}</td>'
        if show_closed_column:
            row += f'<td>{format_date(issue.get("closeDate", "")) if "closeDate" in issue else "-"}</td>'
        tags = issue.get('tags', [])
        row += f'<td>' + ''.join(f'<span class="tag">{html_escape(tag)}</span>' for tag in tags) + ("-" if not tags else "") + '</td>'
        row += f'<td>{html_escape(issue.get("effort", "-"))}</td>'
        row += f'<td>{html_escape(issue.get("debt", "-"))}</td>'
        row += '</tr>'
        rows.append(row)
    return f'<div class="issues-card"><table border="1" class="issues-table">{header}{"".join(rows)}</table></div>' if issues else f'<p>No {status_label} {severity_label} issues.</p>'

# HTML for severity toggles inside a status section
def severity_details(issues_by_sev, status_label):
    html = ''
    show_closed = status_label.lower() == "closed"
    for sev in all_severities:
        sev_issues = issues_by_sev.get(sev, [])
        html += f'<details class="details-modern">\n  <summary>{sev.title()} ({len(sev_issues)})</summary>\n  {issues_table(sev_issues, status_label, sev.title(), show_closed_column=show_closed)}\n</details>\n'
    return html

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sonar Issues Report</title>
{css}
</head>
<body>
<div class="container">
{summary_html}
<details class="details-modern" open>
  <summary>Open Issues ({sum(len(open_issues_by_sev[sev]) for sev in all_severities)})</summary>
  {severity_details(open_issues_by_sev, "open")}
</details>
<details class="details-modern">
  <summary>Closed Issues ({sum(len(closed_issues_by_sev[sev]) for sev in all_severities)})</summary>
  {severity_details(closed_issues_by_sev, "closed")}
</details>
</div>
</body>
</html>'''

with open('sonar-report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML report generated: sonar-report.html")