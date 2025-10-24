## Automation Readiness — API Performance Tests

- Test Case ID: PERF-ORDERS-RAMP-001
  - Title/Description: Ramp-up GET /orders to 1.5× baseline
  - Recommended Action: Automate
  - Justification: API-based, repetitive ramp profile; critical read path; suitable for CI load stage
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-PAYMENT-RAMP-001
  - Title/Description: Ramp-up POST /payment to 2× baseline
  - Recommended Action: Automate
  - Justification: Critical payment flow; regression-prone under ramp; ideal for k6/Gatling
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-SHIPMENT-RAMP-001
  - Title/Description: Ramp-up PUT /shipment to 2× baseline
  - Recommended Action: Automate
  - Justification: API write path; concurrency-sensitive; repeatable ramp
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-ORDERS-SPIKE-001
  - Title/Description: Spike GET /orders 3× for 5 min
  - Recommended Action: Automate
  - Justification: Short, repeatable spike; validates autoscaling and caching
  - Estimated Automation Effort: Low

- Test Case ID: PERF-PAYMENT-SPIKE-001
  - Title/Description: Spike POST /payment 2.5× for 3 min
  - Recommended Action: Automate
  - Justification: Critical payment spike behavior; idempotency/retry checks
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-SHIPMENT-SPIKE-001
  - Title/Description: Spike PUT /shipment 3× for 3 min
  - Recommended Action: Automate
  - Justification: API-based, repeatable spike; detects DB lock/contention issues
  - Estimated Automation Effort: Low

- Test Case ID: PERF-ORDERS-SOAK-001
  - Title/Description: Soak GET /orders at baseline for 4 hours
  - Recommended Action: Automate
  - Justification: Long-running stability/leak detection; fully scriptable
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-PAYMENT-SOAK-001
  - Title/Description: Soak POST /payment baseline for 2 hours
  - Recommended Action: Automate
  - Justification: Critical path; sustained throughput; settlement/idempotency checks
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-SHIPMENT-SOAK-001
  - Title/Description: Soak PUT /shipment baseline for 3 hours
  - Recommended Action: Automate
  - Justification: API writes over time; replication/lag monitoring; repeatable
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-ORDERS-RECOV-001
  - Title/Description: Timeout injection + retry GET /orders
  - Recommended Action: Automate
  - Justification: API retry/circuit behavior; regression-prone under faults
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-PAYMENT-RECOV-001
  - Title/Description: 429/5xx burst + backoff POST /payment
  - Recommended Action: Automate
  - Justification: Critical payment resiliency; idempotency + backoff verification
  - Estimated Automation Effort: Medium

- Test Case ID: PERF-SHIPMENT-RECOV-001
  - Title/Description: DB contention + retry PUT /shipment
  - Recommended Action: Automate
  - Justification: API conditional writes/retry logic; repeatable fault injection
  - Estimated Automation Effort: Medium

