# IO-139525 — Test Cases

- **Test Case ID:** IO-139525-FUNC-001
- **Title/Description:** Functional — Validate heap profiler upload flow with SDK v3 s3-util
- **Preconditions:** Profiler flag enabled; valid S3 bucket/region; creds configured
- **Test Steps:**
  - Start service and trigger capture
  - Verify S3 upload initiated and completed
  - Retrieve object metadata
- **Test Data:** S3 bucket=qa-heap, region=us-east-1; sample profile 10MB
- **Expected Result:** 200 OK; object exists; metadata/tags set
- **Actual Result:**
- **Status:**
- **Postconditions:** Object cleaned or retained per policy
- **Tags/Labels:** API, Regression, Backend
- **Test Type:** Functional

- **Test Case ID:** IO-139525-EDGE-001
- **Title/Description:** Edge — Multipart upload for very large profile (500MB)
- **Preconditions:** Multipart threshold configured; bucket write capacity sized
- **Test Steps:**
  - Generate 500MB profile; trigger upload
  - Monitor parts and completion
- **Test Data:** profile_size=500MB; SSE-S3 enabled
- **Expected Result:** Multipart succeeds; no OOM; ETag present
- **Actual Result:**
- **Status:**
- **Postconditions:** Remove large test object
- **Tags/Labels:** API, Edge, Backend
- **Test Type:** Integration

- **Test Case ID:** IO-139525-INT-001
- **Title/Description:** Integration — SSE-KMS encryption + metadata tagging
- **Preconditions:** KMS key available; IAM permissions granted
- **Test Steps:**
  - Configure SSE-KMS and tags; upload profile
  - Validate metadata/tags on object
- **Test Data:** kms_key=alias/qa-heap; tags=service=io,env=qa
- **Expected Result:** KMS key id on object; tags present
- **Actual Result:**
- **Status:**
- **Postconditions:** None
- **Tags/Labels:** API, Security, Backend
- **Test Type:** Integration


