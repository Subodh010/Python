from bs4 import BeautifulSoup
import requests
import json
import time

keywords = ["election", "voters", "voting", "politics"]
websites = [
    #some urls like ekantipur dont work
    "https://kathmandupost.com",
    "https://ekantipur.com",
    "https://www.thehimalayantimes.com"
]

for site in websites:
    clean_site = site.strip()
    response = requests.get(clean_site)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    seen = set()
    
    for link in soup.find_all("a", href=True):
        if len(articles) >= 5:
            break
            
        text = link.get_text().strip()
        href = link["href"].strip()
        
        # Skip empty text or links without text
        if not text:
            continue
            
        if href in seen:
            continue
            
        # Check if any keyword is in the link text
        if any(kw in text.lower() for kw in keywords):
            seen.add(href)
            
            # Construct full URL
            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                full_url = clean_site.rstrip("/") + href
            else:
                full_url = clean_site.rstrip("/") + "/" + href
            
            try:
                article_resp = requests.get(full_url)
                article_soup = BeautifulSoup(article_resp.text, "html.parser")
                
                paragraphs = article_soup.find_all("p")
                desc = ""
                count = 0
                for p in paragraphs:
                    if count >= 3:
                        break
                    desc += p.get_text().strip() + " "
                    count += 1
                
                # Only add if we got some description
                if desc:
                    articles.append({
                        "title": text,
                        "url": full_url,
                        "description": desc.strip()
                    })
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"Error fetching {full_url}: {e}")
                continue
    
    # Use your original filename generation
    sitename = clean_site[8:]
    filename = sitename + ".json"
    
    #add to json file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(articles)} articles to {filename}")
    time.sleep(2)