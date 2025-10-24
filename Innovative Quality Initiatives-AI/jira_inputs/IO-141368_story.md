# IO-141368 — [UI] Update behaviour of Path to records in HTTP response body and add First record contains headers checkbox

## Details
- Key: IO-141368
- Status: Done
- Labels: 
- Components: UI
- Epic Link: IO-129419
- FixVersions: 2025.9.1

## Description
Path to records in HTTP response body should not be mandatory when the batchSize > 1

Unable to embed resource: AD_4nXcLw2-7ZoXBEEODf_ulAzPwrCCGu2qWHX__2y4ArVxirgG8glQuKRazn7U8LULYkxkQwWa8Cerjk0IIeCknoUN_HFCCr_DvQIgwvwJytZFA2TZ7yOWBXMj6J3ivgrtxJaz8yX5rgQ_key=wzFIyjzVPWfoia9uOuSm4g of type application/octet-stream

When “Override request media type” is set to plain/text in the import, the “Number of records per HTTP request” should show.

Unable to embed resource: AD_4nXcW0Y-H8s3hyqg7xZzAPII3iYk6BR4rGvasWAmzLwDgxF5md9CJGwhWMfQP9e47Rh9AhxFkgiApkZySfVuxyb6IKuAHfnaPJnkgJUaOY5Xo-9K2FEje12G3BeTkNe5hRpCcjZlQBw_key=wzFIyjzVPWfoia9uOuSm4g of type application/octet-stream

Add the below checkbox in the import as well (First Record contains header)

BE field: import.http.response.hasHeader

Unable to embed resource: AD_4nXe617QS-Q_JLLzRGPlo0fiDcBj7xiq6MILUs6-XgKcr4XNmbBOpOe4ptgxyFgIsS_daumXTets5tGgRObuOJ19H4YpqJ1rcC4Sx5WlPItUX4nTH98vsGUlODSoX2XibPvFhsglH_key=wzFIyjzVPWfoia9uOuSm4g of type application/octet-stream

## Acceptance Criteria
(not specified)

## Linked PRs
- https://github.com/celigo/integrator-ui/pull/12528 — IO-141368-updated changes