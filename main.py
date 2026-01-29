from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
# from ollama import Client
from google import genai
import os
from dotenv import load_dotenv
import re
import time
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from datetime import datetime
import msal
import markdown


def scrape_titles(url: str) -> List[Tuple[str, str, str]]:
    """
    Scrape article titles, article URLs, and comments URLs from a given webpage.
    
    Args:
        url: The URL to scrape
        
    Returns:
        A list of tuples containing (title, article_url, comments_url) triplets
        Returns empty list on error
    """
    try:
        # Validate URL format
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            print(f"Error: Invalid URL format: {url}")
            return []
        
        # Set up headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Make the request with timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all titles (Hacker News specific structure)
        titles = []
        
        # Find all story rows with class "athing" - each has an id attribute with the item ID
        story_rows = soup.find_all('tr', class_='athing')
        
        for row in story_rows:
            # Get the item ID from the row
            item_id = row.get('id', '')
            
            # Find the titleline span within this row
            titleline_span = row.find('span', class_='titleline')
            
            if titleline_span and item_id:
                # Find the link within the titleline span
                link = titleline_span.find('a')
                if link:
                    title_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # Convert relative URLs to absolute URLs
                    if href:
                        article_url = urljoin(url, href)
                        # Construct the comments URL using the item ID
                        comments_url = f"https://news.ycombinator.com/item?id={item_id}"
                        titles.append((title_text, article_url, comments_url))
        
        print(f"Successfully scraped {len(titles)} titles from {url}")
        return titles
        
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out for URL: {url}")
        return []
    except requests.exceptions.ConnectionError:
        print(f"Error: Failed to connect to URL: {url}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error: Unexpected error occurred: {e}")
        return []


def scrape_article_and_comments(article_url: str, comments_url: str) -> Tuple[str, str]:
    """
    Scrape full text content from both an article page and its Hacker News comments page.
    
    Args:
        article_url: URL of the article to scrape
        comments_url: URL of the Hacker News comments page
        
    Returns:
        A tuple containing (article_text, comments_text)
        Returns empty strings for any failed scrapes
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Scrape article content
    article_text = ""
    try:
        response = requests.get(article_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, and navigation elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find main content areas (common patterns)
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'content|article|post'))
        
        if main_content:
            article_text = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body text
            article_text = soup.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        article_text = re.sub(r'\n\s*\n', '\n\n', article_text)
        article_text = re.sub(r' +', ' ', article_text)
        
    except Exception as e:
        print(f"Error scraping article {article_url}: {e}")
        article_text = ""
    
    # Scrape Hacker News comments
    comments_text = ""
    try:
        response = requests.get(comments_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all comment containers
        comments = []
        comment_elements = soup.find_all('div', class_='comment')
        
        for comment in comment_elements:
            # Extract comment text
            comment_span = comment.find('span', class_='commtext')
            if comment_span:
                comment_text = comment_span.get_text(separator=' ', strip=True)
                comments.append(comment_text)
        
        comments_text = '\n\n---\n\n'.join(comments)
        
    except Exception as e:
        print(f"Error scraping comments {comments_url}: {e}")
        comments_text = ""
    
    return article_text, comments_text


def parse_ai_response(response_text: str) -> List[int]:
    """
    Parse the AI response to extract article index numbers.
    
    Args:
        response_text: The AI's response containing article indexes
        
    Returns:
        List of integer indexes
    """
    # Remove quotes and extract numbers
    numbers = re.findall(r'\d+', response_text)
    return [int(num) for num in numbers]


def call_gemini_with_retry(client, prompt: str, max_retries: int = 3) -> str:
    """
    Call Gemini API with exponential backoff retry on 503 errors.
    
    Args:
        client: The Gemini client
        prompt: The prompt to send
        max_retries: Maximum number of retries (default 3)
        
    Returns:
        The response text from Gemini
        
    Raises:
        Exception: If all retries fail
    """
    retry_delays = [1, 2, 4]  # Exponential backoff: 1s, 2s, 4s
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
            )
            return response.text
            
        except Exception as e:
            error_str = str(e)
            # Check if it's a 503 error
            if '503' in error_str or 'overloaded' in error_str.lower():
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    delay = retry_delays[attempt]
                    print(f"    Model overloaded (503). Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    print(f"    Failed after {max_retries} attempts.")
                    raise
            else:
                # For non-503 errors, raise immediately
                raise
    
    # This shouldn't be reached, but just in case
    raise Exception("Max retries exceeded")


def render_newsletter_email(summaries: List[dict], keywords: List[str], total_articles: int) -> str:
    """
    Render the newsletter HTML email using Jinja2 template.
    
    Args:
        summaries: List of article summary dictionaries
        keywords: List of keyword strings
        total_articles: Total number of articles analyzed
        
    Returns:
        Rendered HTML email as a string
    """
    try:
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('email_template.html')
        
        # Generate newsletter title based on keywords
        if keywords:
            keyword_str = " & ".join(keywords)
            newsletter_title = f"Your {keyword_str} Newsletter"
        else:
            newsletter_title = "Your Tech Newsletter"
        
        # Format current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Convert markdown summaries to HTML
        processed_summaries = []
        for summary in summaries:
            processed_summary = summary.copy()
            # Convert markdown to HTML
            processed_summary['summary'] = markdown.markdown(
                summary['summary'],
                extensions=['extra', 'nl2br', 'sane_lists']
            )
            processed_summaries.append(processed_summary)
        
        # Render the template
        html_content = template.render(
            newsletter_title=newsletter_title,
            date=current_date,
            keywords=keywords,
            total_articles=total_articles,
            selected_count=len(summaries),
            articles=processed_summaries
        )
        
        return html_content
        
    except TemplateNotFound:
        print("Error: email_template.html not found")
        return ""
    except Exception as e:
        print(f"Error rendering email template: {e}")
        return ""


def send_newsletter_email(html_content: str, recipients: List[str], subject: str) -> bool:
    """
    Send newsletter email using Microsoft Graph API.
    
    Args:
        html_content: Rendered HTML email content
        recipients: List of email addresses
        subject: Email subject line
        
    Returns:
        Boolean indicating success/failure
    """
    try:
        # Load credentials from environment
        client_id = os.getenv("CLIENT_ID")
        tenant_id = os.getenv("TENANT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        sender_email = os.getenv("SENDER_EMAIL")
        
        # Validate required environment variables
        if not all([client_id, tenant_id, client_secret, sender_email]):
            print("Error: Missing required environment variables (CLIENT_ID, TENANT_ID, CLIENT_SECRET, SENDER_EMAIL)")
            return False
        
        # Authenticate with Microsoft Graph API
        print("    Authenticating with Microsoft Graph API...")
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret
        )
        
        # Acquire token
        token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" not in token_response:
            print(f"    Error: Failed to acquire access token: {token_response.get('error_description', 'Unknown error')}")
            return False
        
        access_token = token_response['access_token']
        print("    ✓ Access token acquired successfully")
        
        # Prepare email data
        to_recipients = [{"emailAddress": {"address": recipient}} for recipient in recipients]
        
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_content
                },
                "toRecipients": to_recipients
            }
        }
        
        # Send email via Graph API
        print("    Sending via Graph API endpoint...")
        endpoint = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(endpoint, json=email_data, headers=headers)
        
        if response.status_code == 202:
            for recipient in recipients:
                print(f"    ✓ Successfully sent to {recipient} (HTTP 202)")
            return True
        else:
            print(f"    Error: Failed to send email (HTTP {response.status_code})")
            print(f"    Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"    Error sending email: {e}")
        return False


if __name__ == "__main__":
    # Load environment variables and initialize Gemini client
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Test the scraper with Hacker News
    test_url = "https://news.ycombinator.com/"
    print(f"Scraping titles from: {test_url}\n")
    
    results = scrape_titles(test_url)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} articles:\n")
        for i, (title, article_url, comments_url) in enumerate(results[:10], 1):  # Show first 10
            print(f"{i}. {title}")
            print(f"   Article: {article_url}")
            print(f"   Comments: {comments_url}\n")
    else:
        print("No titles found or an error occurred.")


    keywords = [ "Gaming"]
    
    # Read the newsletter prompt context
    with open('newsletter_prompt_context.md', 'r', encoding='utf-8') as f:
        prompt_context = f.read()
    
    # Build the titles list as a formatted string
    titles_text = ""
    for i, (title, article_url, comments_url) in enumerate(results, 1):
        titles_text += f"{i}. {title}\n"
        titles_text += f"   Article: {article_url}\n"
        titles_text += f"   Comments: {comments_url}\n\n"
    
    # Build the keywords string
    keywords_text = ", ".join(keywords)
    
    # Combine everything into the final prompt
    full_prompt = f"""{prompt_context}

TITLES TO ANALYZE:
{titles_text}

KEYWORDS: {keywords_text}
"""
    
    # Make the Gemini API call
    print("\n" + "="*80)
    print("Calling Gemini API to analyze articles...")
    print("="*80 + "\n")
    
    # # Ollama version (commented out)
    # client = Client(
    #     host='http://192.168.11.81:11434',
    #     headers={'x-some-header': 'some-value'}
    # )
    # response = client.chat(model='qwen3:8b', messages=[
    #     {
    #         'role': 'user',
    #         'content': full_prompt,
    #     },
    # ])
    
    response_text = call_gemini_with_retry(client, full_prompt)
    
    print("AI Response:")
    print("-" * 80)
    print(response_text)
    print("-" * 80)
    
    # Parse the AI response to get selected article indexes
    selected_indexes = parse_ai_response(response_text)
    print(f"\nSelected article indexes: {selected_indexes}\n")
    
    if not selected_indexes:
        print("No articles were selected by the AI.")
    else:
        print("="*80)
        print(f"Processing {len(selected_indexes)} selected articles...")
        print("="*80 + "\n")
        
        summaries = []
        
        for idx in selected_indexes:
            # Convert 1-based index to 0-based
            array_idx = idx - 1
            
            # Validate index
            if array_idx < 0 or array_idx >= len(results):
                print(f"Warning: Index {idx} is out of range. Skipping.")
                continue
            
            title, article_url, comments_url = results[array_idx]
            
            print(f"\n[{idx}] Processing: {title}")
            print(f"    Article URL: {article_url}")
            print(f"    Comments URL: {comments_url}")
            
            # Scrape article and comments
            print(f"    Scraping content...")
            article_text, comments_text = scrape_article_and_comments(article_url, comments_url)
            
            if not article_text and not comments_text:
                print(f"    Failed to scrape content. Skipping.")
                continue
            
            # Truncate if too long to avoid token limits
            max_article_length = 5000
            max_comments_length = 3000
            
            if len(article_text) > max_article_length:
                article_text = article_text[:max_article_length] + "\n...[truncated]"
            
            if len(comments_text) > max_comments_length:
                comments_text = comments_text[:max_comments_length] + "\n...[truncated]"
            
            # Create summarization prompt
            summary_prompt = f"""Please provide a concise summary of this article and highlight key discussion points from the comments.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{article_text}

HACKER NEWS COMMENTS:
{comments_text}

Please provide:
1. A brief summary (2-3 sentences) of the article's main points
2. Key insights or interesting perspectives from the comments
3. Why this might be relevant to someone interested in {keywords_text}"""
            
            print(f"    Generating AI summary...")
            
            try:
                # # Ollama version (commented out)
                # summary_response = client.chat(model='qwen3:8b', messages=[
                #     {
                #         'role': 'user',
                #         'content': summary_prompt,
                #     },
                # ])
                # summary = summary_response.message.content
                
                summary = call_gemini_with_retry(client, summary_prompt)
                
                summaries.append({
                    'index': idx,
                    'title': title,
                    'article_url': article_url,
                    'comments_url': comments_url,
                    'summary': summary
                })
                
                print(f"    ✓ Summary generated successfully")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error generating summary: {e}")
                continue
        
        # Display all summaries
        print("\n\n" + "="*80)
        print("FINAL NEWSLETTER SUMMARIES")
        print("="*80 + "\n")
        
        for item in summaries:
            print(f"[{item['index']}] {item['title']}")
            print(f"Article: {item['article_url']}")
            print(f"Comments: {item['comments_url']}")
            print("\nSummary:")
            print(item['summary'])
            print("\n" + "-"*80 + "\n")
        
        # Email generation and sending
        print("\n" + "="*80)
        print("NEWSLETTER EMAIL GENERATION")
        print("="*80 + "\n")
        
        print("Rendering email template...")
        html_content = render_newsletter_email(summaries, keywords, len(results))
        
        if html_content:
            print(f"✓ Email HTML rendered successfully ({len(html_content)} characters)\n")
            
            # Define recipients from environment variable
            recipient_email = os.getenv("RECIPIENT_EMAIL")
            recipients = [recipient_email]
            
            print(f"Preparing to send to {len(recipients)} recipient(s):")
            for recipient in recipients:
                print(f"  - {recipient}")
            print()
            
            # Generate subject line
            keywords_text = ", ".join(keywords)
            current_date = datetime.now().strftime("%B %d, %Y")
            subject = f"Your {keywords_text} Newsletter - {current_date}"
            
            print("Sending newsletter email...")
            print(f"Subject: {subject}\n")
            
            success = send_newsletter_email(html_content, recipients, subject)
            
            if success:
                print("\n" + "="*80)
                print("Newsletter sent successfully!")
                print("="*80)
            else:
                print("\n" + "="*80)
                print("Failed to send newsletter email")
                print("="*80)
        else:
            print("✗ Failed to render email template. Email not sent.")    