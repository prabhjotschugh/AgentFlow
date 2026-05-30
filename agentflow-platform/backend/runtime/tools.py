from langchain_core.tools import tool
import math
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import html

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        # Simple eval for demonstration; in production use a safer parser
        return str(eval(expression, {"__builtins__": None}, {"math": math}))
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Search the web for information."""
    # Placeholder for actual search implementation
    return f"Search result for '{query}': High-quality info about {query} is usually found on tech blogs, Wikipedia, or official docs."

@tool
def url_scraper(url: str) -> str:
    """Extract text content from a given URL to let agents 'read' articles."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:2000] # Return first 2000 chars for context
    except Exception as e:
        return f"Error scraping URL: {str(e)}"

@tool
def current_time_fetcher() -> str:
    """Get the current date and time in IST (Indian Standard Time)."""
    from datetime import datetime, timedelta, timezone
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S (IST)")

@tool
def youtube_transcript(video_url: str) -> str:
    """Fetch the transcript of a YouTube video using yt-dlp for maximum reliability."""
    try:
        import yt_dlp
        print(f"DEBUG: yt-dlp fetching transcript for: {video_url}")
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en.*'], # Fetch English (manual or auto)
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Check for subtitles or automatic captions
            subs = info.get('subtitles') or info.get('automatic_captions')
            if not subs:
                return "❌ Error: No subtitles found for this video. Use `web_search` instead."
            
            # Find an English track or fallback to first available
            en_key = next((k for k in subs.keys() if k.startswith('en')), None)
            if not en_key:
                if subs.keys():
                    en_key = list(subs.keys())[0]
                else:
                    return "❌ Error: No subtitle tracks detected."
            
            # Prefer json3 format for easy parsing
            formats = subs[en_key]
            target_format = next((f for f in formats if f['ext'] == 'json3'), formats[0])
            
            sub_resp = requests.get(target_format['url'])
            full_text = ""
            
            if target_format['ext'] == 'json3':
                data = sub_resp.json()
                for event in data.get('events', []):
                    if 'segs' in event:
                        for seg in event['segs']:
                            full_text += seg.get('utf8', '')
            else:
                # Basic cleanup for other formats (VTT/SRV)
                clean_text = re.sub(r'<[^>]+>', ' ', sub_resp.text)
                full_text = html.unescape(clean_text)
            
            # Return cleaned text limited to 6000 chars for LLM context
            return re.sub(r'\s+', ' ', full_text).strip()[:6000]

    except Exception as e:
        print(f"DEBUG: yt-dlp tool error: {e}")
        return f"CRITICAL: The transcript tool failed: {str(e)}. ACTION: Use `web_search` to find content for URL: {video_url}"

# Exported list of tools
AVAILABLE_TOOLS = {
    "calculator": calculator,
    "web_search": web_search,
    "url_scraper": url_scraper,
    "current_time_fetcher": current_time_fetcher,
    "youtube_transcript": youtube_transcript
}
