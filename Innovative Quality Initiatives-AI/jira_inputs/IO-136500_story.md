# IO-136500 — [BE] - Context Aware Response Part - 1

## Details
- Key: IO-136500
- Status: Done
- Labels: 
- Components: AI/ML - BE
- Epic Link: IO-132154
- FixVersions: 2025.9.1

## Description
As a user on any page, I want Copilot to know exactly which page I’m viewing, so that I get relevant instructions without describing my location.

Pay load
{

  "query": "How do I add a source?",

  "ui_image": "<base64-encoded-image>",

   “url”:”url”,
   "context_aware": true,

   "context_value":"None"/ "Already Extracted Context"

  "return_sources": true,

   "max_sources": 3,

   "response_format": "markdown",

   "stream": true,

   "thread_id":"thread_KlXyztkFpPxpRyl16gqTFbhD" / "None"

}

Response
#Markdown Text
http://url:5000/v1/gptverse/knowledge-base/answer - post

'data: A flow in Celigo integrator.io is an automated process that connect\n\ndata: s different applications\\n\\nLearn more at:\\n- Flow Docume\n\ndata: s\n\ndata: $$$$---SUGGESTIONS---$$$$\n\ndata: {"suggestions": [{"title": "\\\\n- How to create a flow?\\\\n- What are flow components?\\\\n- How to debug a flow?"}]}\n\ndata: $$$$---LINK---$$$$\n\ndata: [{"link": "https://docs.celigo.com/flow1", "title": "Flow Documentation"}, {"link": "https://docs.celigo.com/flow2", "title": "Flow Examples"}]\n\n'
-----------

#example of a handlebar query 

To use handlebar code in Celigo, the platform offers an intuitive way to create and refine handlebars expressions using plain English prompts. The Celigo AI assistant helps you generate handlebars expressions for various use cases, including handling JSON data and performing calculations. Examples include concatenating strings, capitalizing text, or multiplying numeric values.

## Demonstration of Using Handlebars in Celigo

1. **Generate handlebars using plain prompts**  
   - Begin by describing the desired handlebars output in plain English.  
   - Celigo AI will generate the handlebars expression automatically in the editor. For instance:  
     - Prompt: "Capitalize all words in type field"  
       Handlebars: `{{capitalizeAll type}}`

2. **Refine handlebars with additional prompts**  
   - After creating the initial handlebars, further refine or change it through follow-up prompts.  
   - Example: Add fields or remove data dynamically—like removing a country from an address template.

3. **Preview and test output**  
   - Use the preview option to ensure that your handlebars work as intended. Sample JSON data can be used to test if the expression outputs the correct result.  
   - Example: Concatenate address fields:
     - JSON:  
       ```json
       { "address": { "street_address": "123 Main St", "city": "Anytown", "state": "CA" }}
       ```
     - Handlebars: `{{address.street_address}}, {{address.city}}, {{address.state}}`  
       Output: `123 Main St, Anytown, CA`

4. **Complex operations**  
   - For advanced use cases, you can perform calculations or iterate through data fields.  
     - Example: Multiply price and quantity:
       ```handlebars
       {{#each orders}} {{#each items}} {{multiply price quantity}} {{/each}} {{/each}}
       ```
       Output: Total price for products.

5. **Explain handlebars functionality**  
   - Use Celigo AI's "Explain selection" feature to understand the purpose of specific handlebars expressions or troubleshoot$$$$---SUGGESTIONS---$$$${"suggestions": [{"title": "Use Celigo AI to generate handlebars templates for your use case."}, {"title": "Test refined handlebars expressions with sample JSON structures."}, {"title": "Leverage handlebars for looping, modifying, and calculating within integration flows"}]}$$$$---LINK---$$$$[{"link": "https://docs.celigo.com/hc/en-us/articles/19845101172507-Create-or-explain-handlebars-using-Celigo-AI-component", "title": "Create or explain handlebars using Celigo AI component"}, {"link": "https://docs.celigo.com/hc/en-us/articles/360048995431-Publish-or-unpublish-templates-and-integration-apps", "title": "Publish or unpublish templates and integration apps"}, {"link": "https://docs.celigo.com/hc/en-us/articles/13659882559515-Customization", "title": "Customization"}, {"link": "https://docs.celigo.com/hc/en-us/articles/25951095481755-Chat-with-the-knowledge-bot", "title": "Chat with the knowledge bot"}, {"link": "https://docs.celigo.com/hc/en-us/articles/4414582961819-Learn-how-to-make-the-most-of-your-free-trial", "title": "Learn how to make the most of your free trial"}]

We will stream response, Link of the Documents, 

Headers - Context Value (Might be possible we will pass context and thread id) - Suggestions Questions , 

Regenerate - query, thread id, context_value, url

## Acceptance Criteria
- Begin by describing the desired handlebars output in plain English.
- Celigo AI will generate the handlebars expression automatically in the editor. For instance:
- Prompt: "Capitalize all words in type field"
- After creating the initial handlebars, further refine or change it through follow-up prompts.
- Example: Add fields or remove data dynamically—like removing a country from an address template.

## Linked PRs
- https://github.com/celigo/gptverse/pull/682 — Context3