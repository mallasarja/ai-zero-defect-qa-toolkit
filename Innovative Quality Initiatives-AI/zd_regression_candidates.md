# Zendesk Regression Test Candidates (match ≥1 condition)

Total matches: 102

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254150
https://celigosuccess.zendesk.com/agent/tickets/254165
  - Jira ID: https://celigo.atlassian.net/browse/IO-137331
  - Summary: its multipart issue - https://celigo.atlassian.net/browse/IO-137331, resolved now by releasing hotfix
  - Why: Type=BUG, Regression/Escape, No test case, Caused by release=True, Resolution mentions fix/hotfix/revert, Valid Jira link
  - Suggested Filename: ZD-254165.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254314
  - Jira ID: https://celigo.atlassian.net/browse/IO-137331
  - Summary: Fix is already tested in our non-production environment. Issue happens while using multipart form data transfers.
  - Why: Type=BUG, No test case, Caused by release=True, Resolution mentions fix/hotfix/revert, Valid Jira link
  - Suggested Filename: ZD-254314.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254107
  - Jira ID: 
  - Summary: This issue got resolved now,this was releated to recent fix done for timestamp issue
  - Why: Type=BUG, No test case, Caused by release=True, Resolution mentions fix/hotfix/revert
  - Suggested Filename: ZD-254107.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254230
  - Jira ID: https://celigo.atlassian.net/browse/IO-136378
  - Summary: Escalated  ticket for above ticket, need to followup
  - Why: Type=BUG, No test case, Resolution mentions fix/hotfix/revert, Valid Jira link
  - Suggested Filename: ZD-254230.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254114
  - Jira ID: https://celigo.atlassian.net/browse/IO-138513
  - Summary: Bug got created for this issue.
  - Why: Type=BUG, No test case, Valid Jira link
  - Suggested Filename: ZD-254114.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254136
  - Jira ID: https://celigo.atlassian.net/browse/IO-133578
  - Summary: SFNSIA cloning issue to sandbox, there were bug created[https://celigo.atlassian.net/browse/IO-133578]
  - Why: Type=BUG, Regression/Escape, Valid Jira link
  - Suggested Filename: ZD-254136.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254174
  - Jira ID: https://celigo.atlassian.net/browse/IO-135163
  - Summary: there is an already existing bug and  dev is looking into it https://celigo.atlassian.net/browse/IO-135163 https://celigo-internal.slack.com/archives/CTK3RBK1D/p1750977661630009
  - Why: Type=BUG, No test case, Valid Jira link
  - Suggested Filename: ZD-254174.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254283
  - Jira ID: 
  - Summary: As the Product team is already aware and actively working on a fix (currently in non-prod, with a production deployment planned by end of week), there is no need to raise a new bug for this case.
  - Why: No test case, Customer issue=True, Resolution mentions fix/hotfix/revert
  - Suggested Filename: ZD-254283.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254502
  - Jira ID: https://celigo.atlassian.net/browse/IO-138890
  - Summary: Based on our initial analysis of the customer-reported issue , we observed that after the recent Celigo update, the SFTP file is not being generated when a preMap hook encounters a validation error, even though the flow completes with a "Success" status. This behavior is a regression, as the integration was functioning correctly for over a year prior to the update.
  - Why: No test case, Customer issue=True, Valid Jira link
  - Suggested Filename: ZD-254502.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254986
  - Jira ID: 
  - Summary: Looking into this
  - Why: No test case, Customer issue=True, Resolution mentions fix/hotfix/revert
  - Suggested Filename: ZD-254986.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254101
  - Jira ID: 
  - Summary: Solved - This issue appears to be related to the mapper version being used, and we're currently awaiting the customer's confirmation to proceed with further analysis.
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254101.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254137
  - Jira ID: 
  - Summary: Customer ran the flow and it is successful as well , thats the reason they got transactions on to dashboard. Issue here is the ISA number is not being captured properly from the EDI file , as this is not captured properly our code is setting it to all 0's , so the misconfiguration of FDR from customer side is causing this
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254137.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254185
  - Jira ID: 
  - Summary: customer mentioned, by changing handlebar issue is resolved
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254185.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254254
  - Jira ID: 
  - Summary: Seems like Config issue , not a bug — the issue seems to be with the vendor lookup step not returning results for some records during the flow run. This usually happens if the vendor name or code in the data doesn’t exactly match what’s in NetSuite (e.g., extra spaces, different casing, or missing filters). When the lookup fails, the vendor internal ID stays empty, and since it's required, the record gets silently skipped during import. Support team looking into it will check response from customer , will keep an eye on this for further analysis
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254254.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254255
  - Jira ID: 
  - Summary: Its a config issue, customer changed their mappings and monitoring the flows. Its not a issue
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254255.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254262
https://celigosuccess.zendesk.com/agent/tickets/254264 - same above ticket (Support escaltion)
  - Jira ID: 
  - Summary: Flow stuck Issue
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254264 - same above ticket (Support escaltion).md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254324
  - Jira ID: 
  - Summary: Customer deposits are not being created, might be a configuration issue. Nothing specific to release.
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254324.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254341
  - Jira ID: 
  - Summary: Ticket already created for multipart issue
  - Why: No test case, Caused by release=True
  - Suggested Filename: ZD-254341.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254349
  - Jira ID: 
  - Summary: Does not look like issue or blocker for 
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254349.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254356
  - Jira ID: 
  - Summary: Ticket already created for multipart issue
  - Why: No test case, Caused by release=True
  - Suggested Filename: ZD-254356.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254372
  - Jira ID: 
  - Summary: Requested for FlowID of user to analyze further
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254372.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254377
  - Jira ID: 
  - Summary: its due to https://celigo.atlassian.net/browse/IO-137331
  - Why: No test case, Caused by release=True
  - Suggested Filename: ZD-254377.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254404
  - Jira ID: 
  - Summary: working fine from our end - No issue its config issue with  iClient details because the error says "Unauthorized_client"?
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254404.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254457
  - Jira ID: https://celigo.atlassian.net/browse/IO-40170
  - Summary: Enhancement tracker got created.
  - Why: No test case, Valid Jira link
  - Suggested Filename: ZD-254457.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254477
  - Jira ID: 
  - Summary: This is not an issue, we haven’t added support for those docTypes yet
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254477.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254522
  - Jira ID: 
  - Summary: Tried to reproduce, its working fine. it might be customer config related issue
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254522.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254532
  - Jira ID: 
  - Summary: this is expected behaviour, when version is 2 our code tries to create an EDI Transaction, and currently we dont support IB as docType , this support will be provided mostly in August release
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254532.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254602
  - Jira ID: 
  - Summary: Tried to reproduce, its working fine. it might be customer account specific
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254602.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254630
  - Jira ID: 
  - Summary: To get userID and flowID
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254630.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254695
https://celigosuccess.zendesk.com/agent/tickets/254758
https://celigosuccess.zendesk.com/agent/tickets/254755
https://celigosuccess.zendesk.com/agent/tickets/254747
https://celigosuccess.zendesk.com/agent/tickets/254744
https://celigosuccess.zendesk.com/agent/tickets/254799
  - Jira ID: 
  - Summary: Looks like, based on intitial analysis the customers order data got updated for the field updated_at. (Looks some update happened from Shopify side)
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254799.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254777
  - Jira ID: 
  - Summary: Its not a issue, but timeout issue is frequently faced by multiple customers. We can check it in details once we get more details.
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254777.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254789
  - Jira ID: 
  - Summary: Most likely looks like related to same shopify issue, Unexpected orders are importing 
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254789.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254802
https://celigosuccess.zendesk.com/agent/tickets/254792
  - Jira ID: 
  - Summary: not related this release , seems like configration mismatch ,The customer reports that the NetSuite listener is receiving partial records starting around 3–4:15 PM CT yesterday in both Sandbox and Production. .A cloned flow with a NetSuite SQL lookup briefly returned full records, but the issue reoccurred. This may relate to listener timing, confirmation, or config behavior. Support is investigating.
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254792.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254809
  - Jira ID: 
  - Summary: Looks like issue is specific to customer config and data.
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254809.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254810
  - Jira ID: 
  - Summary: need more info,and waiting for the customer response,team has requested for flow zip to debug more
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254810.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254868
  - Jira ID: 
  - Summary: This user is from latest batch of flow branching conversion which we migrated yesterday for given flow ID 623dd048bf23f93f607db5c1 and job ID 687ffa561d31ff077684306d
  - Why: No test case, Resolution mentions fix/hotfix/revert
  - Suggested Filename: ZD-254868.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254969
  - Jira ID: 
  - Summary: Asked for further customer details on this - flowid, userID and diagnostics
  - Why: No test case, Customer issue=True
  - Suggested Filename: ZD-254969.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254991
  - Jira ID: https://celigo.atlassian.net/browse/IO-139547
  - Summary: Unexpected crash 
  - Why: No test case, Valid Jira link
  - Suggested Filename: ZD-254991.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255024
  - Jira ID: https://celigo.atlassian.net/browse/IO-133190
  - Summary: Not related to July Release
  - Why: No test case, Valid Jira link
  - Suggested Filename: ZD-255024.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255236
  - Jira ID: https://celigo.atlassian.net/browse/IO-47029
  - Summary: there is an enhanment tracker in backlog.
  - Why: No test case, Valid Jira link
  - Suggested Filename: ZD-255236.md

- Zendesk Ticket: No issues observed
  - Jira ID: 
  - Summary: 
  - Why: No test case
  - Suggested Filename: ZD-No issues observed.md

- Zendesk Ticket: No major tickets
  - Jira ID: 
  - Summary: 
  - Why: No test case
  - Suggested Filename: ZD-No major tickets.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/253525
  - Jira ID: 
  - Summary: its not related to release
  - Why: No test case
  - Suggested Filename: ZD-253525.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254003
  - Jira ID: 
  - Summary: Its an config issue, not related to release
  - Why: No test case
  - Suggested Filename: ZD-254003.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254005
  - Jira ID: 
  - Summary: This is not related to the IO release
  - Why: No test case
  - Suggested Filename: ZD-254005.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254034
  - Jira ID: 
  - Summary: This is not related to the July IO release, But need to check and address this (Shopify IA)
  - Why: No test case
  - Suggested Filename: ZD-254034.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254085
  - Jira ID: 
  - Summary: This is not related to the July release
  - Why: No test case
  - Suggested Filename: ZD-254085.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254090
  - Jira ID: 
  - Summary: closed,not releated to release
  - Why: No test case
  - Suggested Filename: ZD-254090.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254092
  - Jira ID: 
  - Summary: this is not releated to Release,this is an query
  - Why: No test case
  - Suggested Filename: ZD-254092.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254094
  - Jira ID: 
  - Summary: solved
  - Why: No test case
  - Suggested Filename: ZD-254094.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254104
  - Jira ID: 
  - Summary: Its an config issue, not related to release
  - Why: No test case
  - Suggested Filename: ZD-254104.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254110
  - Jira ID: 
  - Summary: this issue got resolved and closed.
  - Why: No test case
  - Suggested Filename: ZD-254110.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254117
  - Jira ID: 
  - Summary: Not related to the release
  - Why: No test case
  - Suggested Filename: ZD-254117.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254123
  - Jira ID: 
  - Summary: This is expected behavior as per Shopify’s current API Doc (https://shopify.dev/docs/api/admin-graphql/2025-10) and not a defect ,The error is due to the metafield no longer being recognized, and we just need to update the integration to align with Shopify’s supported schema.
  - Why: No test case
  - Suggested Filename: ZD-254123.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254129
  - Jira ID: 
  - Summary: need more info.
  - Why: No test case
  - Suggested Filename: ZD-254129.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254164
  - Jira ID: 
  - Summary: Target service is taking a long time to respond
  - Why: No test case
  - Suggested Filename: ZD-254164.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254170
  - Jira ID: 
  - Summary: Looking into this
  - Why: No test case
  - Suggested Filename: ZD-254170.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254172
  - Jira ID: 
  - Summary: Not related to current release. Looks like a config issue.
  - Why: No test case
  - Suggested Filename: ZD-254172.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254173
  - Jira ID: 
  - Summary: Config related issue, its resolved
  - Why: No test case
  - Suggested Filename: ZD-254173.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254177
  - Jira ID: 
  - Summary: This is a configuration issue. this is not related to current release.
  - Why: No test case
  - Suggested Filename: ZD-254177.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254187
  - Jira ID: 
  - Summary: Looking into this - not related to July release as email domain from NA region which was not deployed by the time issue was reported
  - Why: No test case
  - Suggested Filename: ZD-254187.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254191
  - Jira ID: 
  - Summary: Orders are now pushing normally, no further issues on the flows are observed
  - Why: No test case
  - Suggested Filename: ZD-254191.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254239
  - Jira ID: 
  - Summary: Flow stuck issue at HTTP Import
  - Why: No test case
  - Suggested Filename: ZD-254239.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254268
  - Jira ID: 
  - Summary: Not related to current release. require further data to monitor on this
  - Why: No test case
  - Suggested Filename: ZD-254268.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254285
  - Jira ID: 
  - Summary: Config issue
  - Why: No test case
  - Suggested Filename: ZD-254285.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254286
  - Jira ID: 
  - Summary: Ticket already created for multipart issue
  - Why: No test case
  - Suggested Filename: ZD-254286.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254298
  - Jira ID: 
  - Summary: Configuration issue.
  - Why: No test case
  - Suggested Filename: ZD-254298.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254320
  - Jira ID: 
  - Summary: Ticket already created(need to followup)
  - Why: No test case
  - Suggested Filename: ZD-254320.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254333
  - Jira ID: 
  - Summary: Not related to the release
  - Why: No test case
  - Suggested Filename: ZD-254333.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254339
  - Jira ID: 
  - Summary: shakeer can you please once check this isse - i have the done  initial analysis , Based on initial analysis, the error appears related to license validation behavior where the system blocks custom AS2 connection creation despite the Trading Partner feature being enabled, and it requires further investigation by the dev  team. Based on initial analysis, the behavior is inconsistent with the expected license setup, suggesting a potential issue in license enforcement logic — further validation by the product team is needed to confirm if it’s a bug or not   shakeer response - We have already replied to support rep on this
  - Why: No test case
  - Suggested Filename: ZD-254339.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254344
  - Jira ID: 
  - Summary: Not related to the release.
  - Why: No test case
  - Suggested Filename: ZD-254344.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254346
  - Jira ID: 
  - Summary: following up with the team,CS tracker got created for this issue
  - Why: No test case
  - Suggested Filename: ZD-254346.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254350
  - Jira ID: 
  - Summary: Not related to the release, able to update FTP connection
  - Why: No test case
  - Suggested Filename: ZD-254350.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254361
  - Jira ID: 
  - Summary: Not related to the current release, IA side intermiittent issue/ issue on licensing.
  - Why: No test case
  - Suggested Filename: ZD-254361.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254381
  - Jira ID: 
  - Summary: needed more info.
  - Why: No test case
  - Suggested Filename: ZD-254381.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254405
  - Jira ID: 
  - Summary: Bug already exists, related to SFNSIO clone issue
  - Why: No test case
  - Suggested Filename: ZD-254405.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254419
  - Jira ID: 
  - Summary: Ticket already created for multipart issue
  - Why: No test case
  - Suggested Filename: ZD-254419.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254425
  - Jira ID: 
  - Summary: Not related to release
  - Why: No test case
  - Suggested Filename: ZD-254425.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254460
  - Jira ID: 
  - Summary: Not related to release
  - Why: No test case
  - Suggested Filename: ZD-254460.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254466
  - Jira ID: 
  - Summary: Does not look like issue because of July release
  - Why: No test case
  - Suggested Filename: ZD-254466.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254466
  - Jira ID: 
  - Summary: Not related to july release
  - Why: No test case
  - Suggested Filename: ZD-254466.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254488
  - Jira ID: 
  - Summary: It is caused by an unexpected closure of the connection to Azure Blob Storage, often due to timeouts, network interruptions, or high concurrency during large uploads.
  - Why: No test case
  - Suggested Filename: ZD-254488.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254528
  - Jira ID: 
  - Summary: Shopify IA, Internal error on Flow
  - Why: No test case
  - Suggested Filename: ZD-254528.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254623
  - Jira ID: 
  - Summary: To check if any issue
  - Why: No test case
  - Suggested Filename: ZD-254623.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254625
https://celigosuccess.zendesk.com/agent/tickets/254626
  - Jira ID: 
  - Summary: To check if any issue
  - Why: No test case
  - Suggested Filename: ZD-254626.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254662
  - Jira ID: 
  - Summary: Not an issue from July release changes.
  - Why: No test case
  - Suggested Filename: ZD-254662.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254685
  - Jira ID: 
  - Summary: Flow not consistently sending EDI documents or not confirming delivery ack from HP. To check whether ns saved search issue or as2 acknowledgement issue or config issue.
  - Why: No test case
  - Suggested Filename: ZD-254685.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254726
  - Jira ID: 
  - Summary: This ticket is duplicate of #254802, now its closed
  - Why: No test case
  - Suggested Filename: ZD-254726.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254746
  - Jira ID: 
  - Summary: need more info.config issue,the issue got resolved
  - Why: No test case
  - Suggested Filename: ZD-254746.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254764
  - Jira ID: 
  - Summary: Requested for userID and flowID of the user.
  - Why: No test case
  - Suggested Filename: ZD-254764.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254792
  - Jira ID: 
  - Summary: need more info
  - Why: No test case
  - Suggested Filename: ZD-254792.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254926
  - Jira ID: 
  - Summary: Waiting for further details
  - Why: No test case
  - Suggested Filename: ZD-254926.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254929
  - Jira ID: 
  - Summary: Further inputs from user required
  - Why: No test case
  - Suggested Filename: ZD-254929.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/254992
  - Jira ID: 
  - Summary: able to download audit logs with custom
  - Why: No test case
  - Suggested Filename: ZD-254992.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255002
  - Jira ID: 
  - Summary: not related to this release and This appears to be a configuration or environment-specific issue, not a bug but likely due to misconfiguration in the VAN (EC Grid) routing or 997 template parsing, as the issue could not be reproduced using the same 997 generator from another Celigo account, and debug logs plus EC Grid delivery reports are needed to confirm outbound transmission and inbound parsing behavio
  - Why: No test case
  - Suggested Filename: ZD-255002.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255003
  - Jira ID: 
  - Summary: Slowness issue 
  - Why: No test case
  - Suggested Filename: ZD-255003.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255036
  - Jira ID: 
  - Summary: This is not related to the July release.
  - Why: No test case
  - Suggested Filename: ZD-255036.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255052
  - Jira ID: 
  - Summary: Verified, This is not related to release changes
  - Why: No test case
  - Suggested Filename: ZD-255052.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255061
  - Jira ID: 
  - Summary: This is expected behavior, not a bug, because the Transformation Rules 2.0 engine was intentionally updated to return [null] for fields that are missing or have null values in the input payload, as part of a design change to standardize and unify null handling across transformations. This output accurately represents the state of the input data, and the transformation logic executed without errors or unexpected failures, confirming it operated as intended. The same payload that previously produced different results now returns [null], indicating a controlled change in logic rather than a misconfiguration or system defect. While this led to issues downstream—such as output filters ignoring records or scripts failing—it stemmed from pre-existing flows not handling [null], not from a malfunction in the transformation engine itself. Therefore, although the change introduced breaking behavior, it aligns with the new transformation design
  - Why: No test case
  - Suggested Filename: ZD-255061.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255100
  - Jira ID: 
  - Summary: To have an eye on the ticket
  - Why: No test case
  - Suggested Filename: ZD-255100.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255161
  - Jira ID: 
  - Summary: this is not a issue but likely an intermittent issue caused by the remote server closing the connection (ECONNRESET) or a temporary OAuth token retrieval problem, possibly due to misconfiguration or instability in the remote server or token setup, rather than any defect in Celigo’s HTTP connector.
  - Why: No test case
  - Suggested Filename: ZD-255161.md

- Zendesk Ticket: https://celigosuccess.zendesk.com/agent/tickets/255221
  - Jira ID: 
  - Summary: Issue is not related to july release
  - Why: No test case
  - Suggested Filename: ZD-255221.md

