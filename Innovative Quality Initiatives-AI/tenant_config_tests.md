## Config-Based Test Cases — Multi-Tenant

Tenant A: region=US, featureX=true, autoSync=false
Tenant B: region=EU, featureX=false, autoSync=true

---

### CFG-TNT-A-PLAN-001 — Plan-based permissions (US, FeatureX on, AutoSync off)
- **Test Case ID**: CFG-TNT-A-PLAN-001
- **Title/Description**: Basic vs Pro vs Enterprise capabilities for Tenant A
- **Tenant Type / Config**: Tenant A — region=US, featureX=true, autoSync=false
- **Preconditions**: Seed users for roles (admin, operator, readonly); plans=Basic, Pro, Enterprise
- **Test Steps**:
  - Switch plan=Basic; login as each role; exercise create/edit/delete features
  - Switch plan=Pro; repeat
  - Switch plan=Enterprise; repeat
- **Expected Result**:
  - Basic: limited features; Pro: mid-tier; Enterprise: full; no over-permission
- **Tags**: tenant, config, role, flag
- **Test Type**: Functional

### CFG-TNT-A-ROLE-002 — Role-based logic with FeatureX enabled
- **Test Case ID**: CFG-TNT-A-ROLE-002
- **Title/Description**: Admin vs Operator vs ReadOnly access to FeatureX
- **Tenant Type / Config**: Tenant A — region=US, featureX=true, autoSync=false
- **Preconditions**: FeatureX flag=on
- **Test Steps**:
  - Admin: create/edit/delete entities via FeatureX UI/API
  - Operator: create/edit only
  - ReadOnly: view-only; no mutating endpoints
- **Expected Result**:
  - Permissions enforced; 403 for disallowed operations; audit logs correct
- **Tags**: tenant, config, role, flag
- **Test Type**: Regression

### CFG-TNT-A-FLAG-003 — Feature toggle lifecycle (enable/disable)
- **Test Case ID**: CFG-TNT-A-FLAG-003
- **Title/Description**: Toggle FeatureX at runtime and validate behavior
- **Tenant Type / Config**: Tenant A — region=US, featureX=true→false, autoSync=false
- **Preconditions**: Dynamic flag service available; cache TTL ≤ 60s
- **Test Steps**:
  - With featureX=true, call endpoints/UI paths
  - Disable featureX; wait TTL; retry
- **Expected Result**:
  - Endpoints return 404/feature-disabled; UI hides controls; no stale access
- **Tags**: tenant, config, flag
- **Test Type**: Functional

### CFG-TNT-A-AUTOSYNC-004 — AutoSync disabled respects manual sync only
- **Test Case ID**: CFG-TNT-A-AUTOSYNC-004
- **Title/Description**: Confirm no background sync occurs when autoSync=false
- **Tenant Type / Config**: Tenant A — region=US, featureX=true, autoSync=false
- **Preconditions**: Scheduler active globally
- **Test Steps**:
  - Wait 2 cycles; verify no sync jobs triggered
  - Trigger manual sync; verify single-run execution
- **Expected Result**:
  - No scheduled runs; manual-only execution; metrics reflect manual run
- **Tags**: tenant, config
- **Test Type**: Regression

### CFG-TNT-A-REG-005 — Regional compliance (US data routing)
- **Test Case ID**: CFG-TNT-A-REG-005
- **Title/Description**: Validate US region data residency and logging
- **Tenant Type / Config**: Tenant A — region=US, featureX=true, autoSync=false
- **Preconditions**: Observability enabled; region tags present
- **Test Steps**:
  - Create/read data; trace storage endpoints and logs
- **Expected Result**:
  - Data stored/processed in US endpoints only; no cross-region transfer
- **Tags**: tenant, config, flag, regional
- **Test Type**: Compliance

### CFG-TNT-A-PLAN-006 — Plan upgrade/downgrade migration safety
- **Test Case ID**: CFG-TNT-A-PLAN-006
- **Title/Description**: Upgrade/downgrade without data loss or permission drift
- **Tenant Type / Config**: Tenant A — region=US, featureX=true, autoSync=false
- **Preconditions**: Existing data and jobs
- **Test Steps**:
  - Upgrade Basic→Pro; downgrade Pro→Basic; verify entitlements and running jobs
- **Expected Result**:
  - Entitlements change atomically; no orphaned background tasks
- **Tags**: tenant, config, role
- **Test Type**: Functional

---

### CFG-TNT-B-PLAN-007 — Plan-based permissions (EU, FeatureX off, AutoSync on)
- **Test Case ID**: CFG-TNT-B-PLAN-007
- **Title/Description**: Basic vs Pro vs Enterprise capabilities for Tenant B
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: Seed users for roles; plans available
- **Test Steps**:
  - Validate plan gates with featureX disabled
- **Expected Result**:
  - FeatureX UI/API hidden regardless of plan; other gates enforced
- **Tags**: tenant, config, role, flag
- **Test Type**: Functional

### CFG-TNT-B-ROLE-008 — Role-based logic without FeatureX
- **Test Case ID**: CFG-TNT-B-ROLE-008
- **Title/Description**: Enforce least privilege across roles
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: N/A
- **Test Steps**:
  - Admin/operator/readonly attempt FeatureX endpoints
- **Expected Result**:
  - 404/feature-disabled responses; no leakage via side channels
- **Tags**: tenant, config, role, flag
- **Test Type**: Regression

### CFG-TNT-B-AUTOSYNC-009 — AutoSync enabled schedules background jobs
- **Test Case ID**: CFG-TNT-B-AUTOSYNC-009
- **Title/Description**: Verify scheduled sync cadence and retry policy
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: Scheduler and queue healthy
- **Test Steps**:
  - Observe 3 cycles; induce one transient failure
- **Expected Result**:
  - Jobs start on schedule; failed run retries per policy; no duplicate runs
- **Tags**: tenant, config
- **Test Type**: Functional

### CFG-TNT-B-REG-010 — Regional compliance (EU/GDPR controls)
- **Test Case ID**: CFG-TNT-B-REG-010
- **Title/Description**: Validate GDPR data residency and privacy controls
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: DPA in place; data masking rules active
- **Test Steps**:
  - Create/read/delete personal data; request export/erase
- **Expected Result**:
  - Data stays in EU; export/erase complete within SLA; audit trail present
- **Tags**: tenant, config, regional
- **Test Type**: Compliance

### CFG-TNT-B-PLAN-011 — Plan change effect on AutoSync quotas
- **Test Case ID**: CFG-TNT-B-PLAN-011
- **Title/Description**: Ensure plan limits throttle autosync volume
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: Quota policy configured per plan
- **Test Steps**:
  - Run autosync under Basic vs Pro; measure throughput and throttling
- **Expected Result**:
  - Basic applies tighter quotas than Pro; no starvation
- **Tags**: tenant, config
- **Test Type**: Functional

### CFG-TNT-B-ERROR-012 — Error recovery differences with autosync
- **Test Case ID**: CFG-TNT-B-ERROR-012
- **Title/Description**: Validate retry/backoff with autosync=true
- **Tenant Type / Config**: Tenant B — region=EU, featureX=false, autoSync=true
- **Preconditions**: Backoff policy with jitter
- **Test Steps**:
  - Inject 429/5xx; observe retries and backoff
- **Expected Result**:
  - Bounded retries; success recovery post-transient events
- **Tags**: tenant, config
- **Test Type**: Recovery

