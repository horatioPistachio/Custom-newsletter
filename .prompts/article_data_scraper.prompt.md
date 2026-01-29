# Article Data Scraper Prompt

## Objective
Create a function to scrape full text content from both article pages and their corresponding Hacker News comment pages, then integrate with AI to generate summaries.

## Part 1: Article and Comments Scraper Function

### Function Specifications
- **Function Name**: `scrape_article_and_comments(article_url: str, comments_url: str) -> Tuple[str, str]`
- **Input**: 
  - `article_url`: URL of the article to scrape
  - `comments_url`: URL of the Hacker News comments page
- **Output**: A tuple containing:
  - Element 0: Full text content from the article page (string)
  - Element 1: Full text content from the comments page (string)

### Technical Requirements
- Use `requests` library for HTTP requests
- Use `BeautifulSoup` (bs4) for HTML parsing
- Set appropriate timeouts (10 seconds)
- Use proper User-Agent headers
- Extract only meaningful text content (strip scripts, styles, navigation)
- For article pages: Extract main content text
- For comments pages: Extract all comment text from Hacker News

### Error Handling
Must gracefully handle:
- Network errors (timeouts, connection failures)
- HTTP errors (404, 500, etc.)
- Malformed HTML or missing content
- Return empty strings for failed scrapes
- Log errors without crashing

### Text Extraction Guidelines
- Remove HTML tags and get clean text
- Remove excessive whitespace and normalize spacing
- Preserve paragraph structure where possible
- For HN comments: Extract username, timestamp, and comment text
- Handle nested comment threads appropriately

## Part 2: Integration with Main Workflow

### Integration Requirements
After the initial scraping and AI article selection:

1. **Parse AI Response**
   - Extract article index numbers from AI response (e.g., "6,11,13,24,26")
   - Handle various formats (with/without quotes, with/without spaces)
   - Validate indexes are within range of scraped articles

2. **Scrape Selected Articles**
   - For each article index in the AI response:
     - Retrieve the article_url and comments_url from the original scrape results
     - Call `scrape_article_and_comments()` to get full content
     - Handle failures gracefully (skip articles that fail to scrape)

3. **AI Summarization**
   - For each successfully scraped article:
     - Create a prompt that includes:
       - Article title
       - Article text content
       - Comments content
     - Request AI to generate a concise summary
     - Ask AI to highlight key discussion points from comments
     - Store the summary with the article information

4. **Final Output**
   - Display a numbered list of summaries
   - Each summary should include:
     - Article title
     - AI-generated summary of the article
     - Key insights from the comments section
     - Links to the article and comments

### Error Handling in Integration
- Skip articles that fail to scrape
- Continue processing remaining articles on errors
- Provide clear feedback about which articles were successfully processed
- Handle empty or invalid AI responses

### Expected Flow
```
1. Scrape HN front page → Get all titles
2. AI selects relevant articles → Get index list
3. For each selected article:
   a. Scrape article + comments
   b. Send to AI for summary
   c. Collect summary
4. Display all summaries to user
```

### Performance Considerations
- Process articles sequentially to avoid overwhelming the Ollama API
- Add brief delays between requests if needed
- Provide progress feedback to user during processing
- Limit total articles processed if list is very long (e.g., max 10)