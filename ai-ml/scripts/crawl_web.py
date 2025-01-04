import requests
from bs4 import BeautifulSoup

def crawl_web_content(urls):
    """Crawl and extract content from a list of URLs."""
    crawled_content = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                content = " ".join(paragraphs)
                crawled_content.append({"url": url, "content": content})
                print(f"Successfully crawled: {url}")
            else:
                print(f"Failed to fetch {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    return crawled_content
