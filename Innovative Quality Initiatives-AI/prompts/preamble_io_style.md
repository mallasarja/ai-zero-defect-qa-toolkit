### IO-Style Preamble for Test Generation

#### IO Verbs (use these explicit steps)
- Create Flow
- Configure Import/Export
- Set Mappings
- Run Flow
- Check Dashboard & Logs
- Inspect HTTP/Error payloads

#### Common UI elements and names
- Buttons: Run, Save, Test, Retry
- Tabs: Dashboard, Mappings, Logs, Settings
- Widgets: Status chips (Success, Warning, Error), Throughput charts

#### Dashboard checks
- Verify run status green; no error badges
- Inspect recent runs, throughput, and error logs

#### Error/log locations
- Flow run logs, job IDs, HTTP webhook retries, DLQ if applicable

#### A11y checklist
- Keyboard navigation only; logical focus order
- Visible focus ring; ARIA roles/labels present
- Contrast ratio AA; no keyboard traps


