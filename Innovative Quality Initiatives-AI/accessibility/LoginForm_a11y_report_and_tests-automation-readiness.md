## Automation Readiness — LoginForm Accessibility Tests

- Test Case ID: A11Y-LOGIN-001
  - Title/Description: Keyboard navigation order
  - Recommended Action: Automate (partial)
  - Justification: Keyboard focus order and activation via Playwright/axe-core; stable
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-002
  - Title/Description: Labels and names announced
  - Recommended Action: Automate (partial)
  - Justification: Validate accessible names/description via testing-library/axe
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-003
  - Title/Description: Error announcement (role=alert)
  - Recommended Action: Automate
  - Justification: Programmatically trigger validation; assert role=alert announcement hooks
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-004
  - Title/Description: Live region status announcement
  - Recommended Action: Automate (partial)
  - Justification: Assert DOM updates on status region; SR announcement may need manual confirmation
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-005
  - Title/Description: `aria-invalid` toggling
  - Recommended Action: Automate
  - Justification: Deterministic attribute checks after validation
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-006
  - Title/Description: Help text association via `aria-describedby`
  - Recommended Action: Automate
  - Justification: Inspect attribute concatenation; stable
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-007
  - Title/Description: Color contrast checks
  - Recommended Action: Manual
  - Justification: Requires theme-aware visual validation and contrast tooling
  - Estimated Automation Effort: Medium

- Test Case ID: A11Y-LOGIN-008
  - Title/Description: Focus on first invalid field (enhancement)
  - Recommended Action: Automate (once implemented)
  - Justification: Post-implementation, assert focus lands on first invalid
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-009
  - Title/Description: Link semantics for Forgot password
  - Recommended Action: Automate
  - Justification: Assert valid href/route or button semantics
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-010
  - Title/Description: Checkbox keyboard interaction
  - Recommended Action: Automate
  - Justification: Keyboard toggle + label association verifiable
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-011
  - Title/Description: Required fields announced
  - Recommended Action: Automate (partial)
  - Justification: `aria-required` presence is scriptable; SR phrasing may need manual spot-check
  - Estimated Automation Effort: Low

- Test Case ID: A11Y-LOGIN-012
  - Title/Description: Heading and structural semantics
  - Recommended Action: Automate (partial)
  - Justification: Check `<h1>` presence; landmarks may depend on app shell
  - Estimated Automation Effort: Low

