## API Performance, Load, Stress, and Recovery Test Scenarios

Baseline traffic (approx):
- GET /orders — 6,000 requests/minute (≈100 rps)
- POST /payment — 3,000 requests/minute (≈50 rps)
- PUT /shipment — 2,500 requests/minute (≈42 rps)

Service-level targets (tune per SLOs):
- P50 < 100 ms, P95 < 300 ms, P99 < 800 ms
- Error rate (5xx, timeouts) ≤ 0.5% at baseline; ≤ 1% at peak
- No data loss; idempotency intact; downstream backpressure handled

---

### PERF-ORDERS-RAMP-001 — Ramp-up GET /orders to 1.5× baseline
- **Test Case ID:** PERF-ORDERS-RAMP-001
- **Load Profile:** Ramp 0 → 150 rps over 15 min; hold 15 min
- **Preconditions:** Prod-like data; caches warm allowed; autoscaling enabled
- **Test Steps:**
  - Start at 0 rps; increase linearly to 150 rps in 15 min
  - Hold 150 rps for 15 min; collect metrics and logs
- **Expected Result:**
  - P95 < 300 ms; error rate ≤ 1%; zero saturation errors
  - No throttling from dependencies; ASG scales within policy
- **Tags:** performance, ramp, orders
- **Test Type:** Ramp-up

### PERF-PAYMENT-RAMP-001 — Ramp-up POST /payment to 2× baseline
- **Test Case ID:** PERF-PAYMENT-RAMP-001
- **Load Profile:** Ramp 0 → 100 rps over 20 min; hold 20 min
- **Preconditions:** Payment gateway sandbox; idempotency keys enabled
- **Test Steps:**
  - Ramp to 100 rps; hold
  - Validate no duplicate charges; idempotency headers effective
- **Expected Result:**
  - P95 < 300 ms; charge success ≥ 99%; no duplicates
- **Tags:** performance, ramp, payment
- **Test Type:** Ramp-up

### PERF-SHIPMENT-RAMP-001 — Ramp-up PUT /shipment to 2× baseline
- **Test Case ID:** PERF-SHIPMENT-RAMP-001
- **Load Profile:** Ramp 0 → 84 rps over 20 min; hold 20 min
- **Preconditions:** Shipping provider sandbox; retry-safe updates
- **Test Steps:**
  - Ramp and hold; verify update latency and write amplification
- **Expected Result:**
  - P95 < 350 ms; conflict/409 ≤ 0.5%; retries bounded
- **Tags:** performance, ramp, shipment
- **Test Type:** Ramp-up

---

### PERF-ORDERS-SPIKE-001 — Spike GET /orders 3× for 5 min
- **Test Case ID:** PERF-ORDERS-SPIKE-001
- **Load Profile:** Baseline 100 rps → spike 300 rps (5 min) → baseline
- **Preconditions:** Autoscaling headroom 30%; cache capacity sized
- **Test Steps:**
  - Sustain baseline 5 min; spike to 300 rps for 5 min; drop back
- **Expected Result:**
  - No sustained queue growth; recovery < 2 min to baseline latency
- **Tags:** performance, spike, orders
- **Test Type:** Spike

### PERF-PAYMENT-SPIKE-001 — Spike POST /payment 2.5× for 3 min
- **Test Case ID:** PERF-PAYMENT-SPIKE-001
- **Load Profile:** 50 rps → 125 rps (3 min) → 50 rps
- **Preconditions:** Gateway rate limits known; backoff configured
- **Test Steps:**
  - Spike and observe 429/5xx handling, retry/backoff behavior
- **Expected Result:**
  - No duplicate transactions; retries respect jitter/backoff; success ≥ 98%
- **Tags:** performance, spike, payment
- **Test Type:** Spike

### PERF-SHIPMENT-SPIKE-001 — Spike PUT /shipment 3× for 3 min
- **Test Case ID:** PERF-SHIPMENT-SPIKE-001
- **Load Profile:** 42 rps → 126 rps (3 min) → 42 rps
- **Preconditions:** DB write capacity and index hot paths monitored
- **Test Steps:**
  - Spike; monitor lock contention, 409/412 rates
- **Expected Result:**
  - Conflict rates stable; retries bounded; P95 < 400 ms at peak
- **Tags:** performance, spike, shipment
- **Test Type:** Spike

---

### PERF-ORDERS-SOAK-001 — Soak GET /orders at baseline for 4 hours
- **Test Case ID:** PERF-ORDERS-SOAK-001
- **Load Profile:** Constant 100 rps for 4h
- **Preconditions:** Rolling logs; memory/FD leak monitors
- **Test Steps:**
  - Run 4h; capture resource trends (CPU, mem, GC, threads)
- **Expected Result:**
  - No leaks; steady latencies; error rate ≤ 0.5%
- **Tags:** performance, soak, orders
- **Test Type:** Soak

### PERF-PAYMENT-SOAK-001 — Soak POST /payment baseline for 2 hours
- **Test Case ID:** PERF-PAYMENT-SOAK-001
- **Load Profile:** Constant 50 rps for 2h
- **Preconditions:** Gateway quotas; idempotency metrics
- **Test Steps:**
  - Run 2h; validate idempotency and settlement queues
- **Expected Result:**
  - Stable latencies; no duplicate charges; error ≤ 0.5%
- **Tags:** performance, soak, payment
- **Test Type:** Soak

### PERF-SHIPMENT-SOAK-001 — Soak PUT /shipment baseline for 3 hours
- **Test Case ID:** PERF-SHIPMENT-SOAK-001
- **Load Profile:** Constant 42 rps for 3h
- **Preconditions:** DB autovacuum/index maintenance scheduled off-window
- **Test Steps:**
  - Run 3h; monitor write amplification and replication lag
- **Expected Result:**
  - P95 < 350 ms; replication lag < threshold; error ≤ 0.5%
- **Tags:** performance, soak, shipment
- **Test Type:** Soak

---

### PERF-ORDERS-RECOV-001 — Timeout injection + retry GET /orders
- **Test Case ID:** PERF-ORDERS-RECOV-001
- **Load Profile:** 100 rps with 10% upstream timeouts injected (5 min)
- **Preconditions:** Client timeouts=800 ms; retries=2; backoff=100–300 ms jitter
- **Test Steps:**
  - Run baseline; inject timeouts; observe retry behavior and circuit breaker
- **Expected Result:**
  - Effective retries; overall error ≤ 1%; breaker remains closed or recovers < 60s
- **Tags:** performance, timeout, recovery, orders
- **Test Type:** Recovery

### PERF-PAYMENT-RECOV-001 — 429/5xx burst + backoff POST /payment
- **Test Case ID:** PERF-PAYMENT-RECOV-001
- **Load Profile:** 50 rps; inject 20% 429/5xx for 3 min
- **Preconditions:** Idempotency keys; exponential backoff with jitter
- **Test Steps:**
  - Inject errors; verify backoff, no duplicate charges, final success ≥ 97%
- **Expected Result:**
  - Bounded retries; no double-billing; error converges to baseline post-injection
- **Tags:** performance, timeout, recovery, payment
- **Test Type:** Recovery

### PERF-SHIPMENT-RECOV-001 — DB contention + retry PUT /shipment
- **Test Case ID:** PERF-SHIPMENT-RECOV-001
- **Load Profile:** 42 rps; inject lock contention / 409 for 5 min
- **Preconditions:** Retry-on-409 with max 2 attempts; ETag/If-Match supported
- **Test Steps:**
  - Induce contention; verify conditional updates and retry semantics
- **Expected Result:**
  - Conflict handled via conditional writes; success rate ≥ 98%
- **Tags:** performance, timeout, recovery, shipment
- **Test Type:** Recovery

