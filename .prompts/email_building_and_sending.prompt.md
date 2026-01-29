# Email Building and Sending Prompt

## Objective
Integrate the newsletter generation workflow with email delivery by combining the Jinja2 HTML template, email sending functionality, and AI-generated summaries into a complete automated newsletter system.

## Requirements

### Part 1: Email Template Rendering

#### Function Specifications
- **Function Name**: `render_newsletter_email(summaries: List[dict], keywords: List[str], total_articles: int) -> str`
- **Input**:
  - `summaries`: List of article summary dictionaries (with keys: `index`, `title`, `article_url`, `comments_url`, `summary`)
  - `keywords`: List of keyword strings used for filtering
  - `total_articles`: Total number of articles analyzed
- **Output**: Rendered HTML email as a string

#### Technical Requirements
- Use Jinja2 templating engine to render `email_template.html`
- Pass the following variables to the template:
  - `newsletter_title`: Dynamic title (e.g., "Your Gaming Newsletter")
  - `date`: Current date formatted nicely (e.g., "January 29, 2026")
  - `keywords`: List of keywords
  - `total_articles`: Total articles scraped
  - `selected_count`: Number of articles selected by AI
  - `articles`: The summaries list
- Handle template loading errors gracefully
- Return the rendered HTML string

### Part 2: Email Sending Function

#### Function Specifications
- **Function Name**: `send_newsletter_email(html_content: str, recipients: List[str], subject: str) -> bool`
- **Input**:
  - `html_content`: Rendered HTML email content
  - `recipients`: List of email addresses
  - `subject`: Email subject line
- **Output**: Boolean indicating success/failure

#### Technical Requirements
- Use **Microsoft Graph API** with MSAL authentication for secure email sending
- Load credentials from environment variables:
  - `CLIENT_ID` - Azure AD application (client) ID
  - `TENANT_ID` - Azure AD directory (tenant) ID
  - `CLIENT_SECRET` - Azure AD client secret
  - `SENDER_EMAIL` - Email address to send from (e.g., conor@horatiopistachio.com)
- Authentication flow:
  - Use `msal.ConfidentialClientApplication` with client credentials flow
  - Authority: `https://login.microsoftonline.com/{TENANT_ID}`
  - Scope: `["https://graph.microsoft.com/.default"]`
  - Acquire token using `acquire_token_for_client()`
- Email sending via Graph API:
  - Endpoint: `https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail`
  - Method: POST with Bearer token authentication
  - Content-Type: HTML (`contentType: "HTML"`)
  - Build message structure with subject, HTML body, and recipients
  - Success response: HTTP 202 (Accepted)
- Handle authentication errors gracefully (invalid credentials, expired tokens)
- Handle API errors gracefully (network issues, Graph API errors)
- Return True on success (202 response), False on failure
- Log success/failure for each recipient

### Part 3: Integration into Main Workflow

#### Integration Points
After generating summaries in main.py:

1. **Check if summaries exist**
   - If no summaries were generated, skip email sending
   - Log appropriate message

2. **Render email template**
   - Call `render_newsletter_email()` with the collected data
   - Handle any template rendering errors

3. **Send email to subscribers**
   - Define recipient list (initially just `bigman@gmail.com`)
   - Generate appropriate subject line (e.g., "Your Gaming Newsletter - [Date]")
   - Call `send_newsletter_email()` with rendered HTML
   - Display success/failure message

4. **Progress feedback**
   - Show status messages for each step
   - Display recipient list before sending
   - Confirm successful delivery

### Part 4: Configuration Management

#### Environment Variables Required
Add to `.env` file:
```
# Microsoft Graph API Configuration
CLIENT_ID=your-azure-app-client-id
TENANT_ID=your-azure-tenant-id
CLIENT_SECRET=your-azure-client-secret
SENDER_EMAIL=conor@horatiopistachio.com

# Azure AD App Registration Setup:
# 1. Go to https://portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/RegisteredApps
# 2. Create new app registration
# 3. Get Client ID and Tenant ID from Overview page
# 4. Create Client Secret in "Certificates & secrets"
# 5. Grant API permissions: Mail.Send (Application permission)
# 6. Admin must grant consent for the organization
```

#### Subscriber List Management
- Initially hardcoded: `["bigman@gmail.com"]`
- Should be easily expandable to multiple recipients
- Consider future enhancement: load from file or database

### Part 5: Error Handling

Must handle:
- Template file not found
- Template rendering errors (invalid data structure)
- Missing environment variables (CLIENT_ID, TENANT_ID, CLIENT_SECRET, SENDER_EMAIL)
- MSAL authentication failures (invalid credentials, token acquisition errors)
- Microsoft Graph API errors (HTTP errors, rate limiting)
- Network timeouts and connection issues
- Invalid recipient email addresses
- 401 Unauthorized (invalid or expired token)
- 403 Forbidden (insufficient permissions)
- 429 Too Many Requests (rate limiting)

For each error:
- Log descriptive error message with response status code
- Continue with remaining workflow where possible
- Don't crash the entire application

### Expected Output Flow

```
================================================================================
NEWSLETTER EMAIL GENERATION
================================================================================

Rendering email template...
✓ Email HTML rendered successfully (12,345 characters)

Preparing to send to 1 recipient(s):
  - bigman@gmail.com

Sending newsletter email...
Subject: Your Gaming Newsletter - January 29, 2026

Authenticating with Microsoft Graph API...
✓ Access token acquired successfully

Sending via Graph API endpoint...
✓ Successfully sent to bigman@gmail.com (HTTP 202)

================================================================================
Newsletter sent successfully!
================================================================================
```

### Testing Considerations
- Test with valid Azure AD credentials
- Test with missing .env variables
- Test with invalid recipient addresses
- Verify HTML renders correctly in email clients (especially Outlook)
- Check spam folder if emails don't arrive
- Verify Azure AD app has Mail.Send permission granted
- Ensure admin consent has been granted for the application
- Test with various recipient domains

### Package Dependencies
Add to requirements.txt:
```
jinja2
msal
requests
```

### Implementation Reference
See `email_sender.py` for working Microsoft Graph API example with:
- MSAL authentication using client credentials flow
- Graph API sendMail endpoint usage
- Proper token handling and error checking