# Beautiful Soup Scraper Prompt

## Objective
Create a robust web scraping function in `main.py` using Beautiful Soup to extract article titles and their associated URLs from web pages.

## Requirements

### Function Specifications
- **Function Name**: `scrape_titles(url: str) -> List[Tuple[str, str]]`
- **Input**: A single URL string
- **Output**: A list of tuples where each tuple contains:
  - Element 0: Article title (string)
  - Element 1: Associated URL (string) - should be absolute URLs, not relative paths

### Error Handling
The function must gracefully handle:
- Invalid or malformed URLs
- Network connectivity issues (timeouts, connection errors)
- HTTP errors (404, 500, etc.)
- Missing or malformed HTML content
- Return an empty list or appropriate error message on failure

### Technical Requirements
- Use `requests` library for HTTP requests
- Use `BeautifulSoup` (bs4) for HTML parsing
- Set appropriate timeouts for requests (e.g., 10 seconds)
- Use proper User-Agent headers to avoid blocking
- Handle relative URLs by converting them to absolute URLs

### Test Case
**Primary URL**: https://news.ycombinator.com/

This site contains:
- Story titles in `<span class="titleline">` elements
- Links within those spans to the actual articles
- Both external links and internal Hacker News comment links

### Expected Behavior
1. Successfully fetch the HTML content from the provided URL
2. Parse the HTML to locate all article titles
3. Extract both the title text and the corresponding URL
4. Return a clean list of (title, url) tuples
5. Log or handle errors appropriately without crashing